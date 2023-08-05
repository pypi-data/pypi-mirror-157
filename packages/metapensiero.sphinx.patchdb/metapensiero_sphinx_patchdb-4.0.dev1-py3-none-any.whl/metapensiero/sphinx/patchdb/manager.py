# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Script&Patch Manager
# :Created:   ven 14 ago 2009 13:09:28 CEST
# :Author:    Lele Gaifax <lele@nautilus.homeip.net>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2009, 2010, 2012-2018, 2021 Lele Gaifax
#

from collections import defaultdict
import json
import logging
import pickle
from os.path import dirname, exists, relpath

from .patch import DependencyError, sort_by_constraints


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class DuplicatedScriptError(Exception):
    "Indicates that a script is not unique."


class Missing3rdPartyModule(Exception):
    "Indicates that a 3rd party module is missing"


class _MissingPatchesIterator:
    def __init__(self, manager, context, always_first, missing, always_last):
        self.manager = manager
        self.context = context
        self.always_first = always_first
        self.missing = missing
        self.always_last = always_last

    def __len__(self):
        return len(self.always_first) + len(self.missing) + len(self.always_last)

    def __iter__(self):
        context = self.context
        precedences = self.manager.precedences
        always_first = self.always_first
        missing = self.missing
        always_last = self.always_last
        migrations = {p for p in missing if p.is_migration}

        if always_first:
            logger.info("Applying execute-always-first patches...")
            for patch in sort_by_constraints(always_first, self.manager):
                yield patch

        logger.info("Applying missing patches...")
        while missing:
            # Get rid of already applied scripts

            applied = set()
            for patch in missing:
                if patch.revision == context[patch.patchid]:
                    logger.debug("Skipping %s, already applied", patch)
                    yield None
                    applied.add(patch)

            if applied:
                missing -= applied
                continue

            # Try to apply migration scripts as early as possible

            pending_migrations = {}
            patches = []
            for patch in migrations:
                # Postpone execution if other scripts preceed this ones

                precs = precedences.get((patch.patchid, patch.revision))
                if precs is not None:
                    skip = False
                    for ppatch in precs:
                        current = context[ppatch.patchid]
                        if current is None or current < ppatch.revision:
                            logger.debug("Postponing %s, must follow %s which is"
                                         " currently at %s", patch, ppatch, current)
                            skip = True
                            break
                    if skip:
                        continue

                # Take note about what this migration is bringing, so that we can postpone the
                # execution of those patches, giving an higher priority to the migration itself

                for depid, deprev in patch.brings:
                    pending_migrations[(depid, deprev)] = patch

                # Consider patch dependencies: postpone execution if they are not yet met, skip
                # it if we are beyond the requested revisions

                for depid, deprev in patch.depends:
                    current = context[depid]
                    if current is None or current < deprev:
                        logger.debug("Postponing %s, depends on '%s@%s' but it's at %s",
                                     patch, depid, deprev, current)
                        break
                    elif current is not None and current > deprev:
                        logger.debug("Skipping %s, depends on '%s@%s' but it's already at %s",
                                     patch, depid, deprev, current)
                        yield None
                        applied.add(patch)
                        break
                else:
                    # Skip migration script when what it brings is already there

                    for depid, deprev in patch.brings:
                        current = context[depid]
                        if current is not None and current >= deprev:
                            logger.debug("Skipping %s, brings '%s@%s' but it's already at %s",
                                         patch, depid, deprev, current)
                            yield None
                            applied.add(patch)
                            break
                    else:
                        patches.append(patch)
            if patches:
                for patch in sort_by_constraints(patches, self.manager):
                    yield patch
                    applied.add(patch)

            if applied:
                missing -= applied
                migrations -= applied
                continue

            # Normal scripts

            patches = []
            for patch in missing:
                precs = precedences.get((patch.patchid, patch.revision))
                if precs is not None:
                    skip = False
                    for ppatch in precs:
                        current = context[ppatch.patchid]
                        if current is None or current < ppatch.revision:
                            logger.debug("Postponing %s, must follow %s which is"
                                         " currently at %s", patch, ppatch, current)
                            skip = True
                            break
                    if skip:
                        continue

                if (patch.patchid, patch.revision) in pending_migrations:
                    logger.debug("Postponing %s, will be brough by %s",
                                 patch, pending_migrations[(patch.patchid, patch.revision)])
                    continue

                for depid, deprev in patch.depends:
                    current = context[depid]
                    if current is None or current < deprev:
                        logger.debug("Postponing %s, depends on '%s@%s' but it's at %s",
                                     patch, depid, deprev, current)
                        break
                    elif current is not None and current > deprev:
                        logger.debug("Skipping %s, depends on '%s@%s' but it's already at %s",
                                     patch, depid, deprev, current)
                        yield None
                        applied.add(patch)
                        break
                else:
                    patches.append(patch)
            if patches:
                for patch in sort_by_constraints(patches, self.manager):
                    yield patch
                    applied.add(patch)

            if not applied:
                if all(p.is_migration for p in missing):
                    for patch in missing:
                        yield None
                    break
                else:
                    logger.critical('Could not apply %d scripts', len(missing))

                    # This will raise a CircularDependencyError, if the problem is due to
                    # dependency cycles.

                    sort_by_constraints(missing, self.manager)

                    # If that's not the case, list the remaining scripts for debug

                    for patch in missing:
                        logger.warning('- %s', patch)
                    raise DependencyError('Could not apply %d scripts, probably due to'
                                          ' non-meetable dependencies' % len(missing))

            missing -= applied

        if always_last:
            logger.info("Applying execute-always-last patches...")
            for patch in sort_by_constraints(always_last, self.manager):
                yield patch


class PatchManager:
    """
    An instance of this class collects a set of patches and acts as
    a dictionary. It's able to serialize the patches taking into
    account the dependencies.
    """

    def __init__(self):
        self.db = {}
        self.precedences = defaultdict(set)

    def __getitem__(self, patchid):
        """
        Return the patch given its `patchid`, or ``None`` if it does not exist.
        """
        return self.db.get(patchid)

    def __setitem__(self, patchid, patch):
        """
        Register the given `patch` identified by `patchid`.
        """
        self.db[patchid] = patch

    def __iadd__(self, patch):
        self.db[patch.patchid] = patch
        return self

    def neededPatches(self, context):
        """
        Return an iterator over *applicable* patches, in the
        right order to satisfy their inter-dependencies.
        """

        missing = set()
        always_first = set()
        always_last = set()
        precedences = self.precedences

        logger.debug("Collecting and ordering patches...")
        for pid, patch in self.db.items():
            patch.adjustUnspecifiedRevisions(self)

            applicable, reason = patch.isApplicable(context)
            if applicable:
                for preceed in patch.preceeds:
                    precedences[preceed].add(patch)

                if patch.always:
                    if patch.always == 'first':
                        always_first.add(patch)
                    else:
                        always_last.add(patch)
                else:
                    missing.add(patch)
            else:
                logger.debug("Ignoring %s: %s", patch, reason)

        return _MissingPatchesIterator(self, context, always_first, missing, always_last)


class PersistentPatchManager(PatchManager):
    """
    Patch manager that uses a Pickle/JSON file as its persistent storage.
    """

    def __init__(self, storage_path=None):
        super().__init__()
        if isinstance(storage_path, str):
            self.storages = [storage_path]
        else:
            self.storages = storage_path

    def _checkMissingRevisionsBump(self):
        old_db = self._load()
        if not old_db:
            return

        for patch in self.db.values():
            old = old_db.get(patch.patchid)
            if old is not None:
                if old.revision == patch.revision and old.script != patch.script:
                    logger.warning("The %s has been modified, but the revision did not", patch)

    def save(self):
        self._checkMissingRevisionsBump()

        storage_path = self.storages[0]
        if storage_path is None:
            return

        logger.debug("Writing patches to %s", storage_path)
        spendswith = storage_path.endswith
        if storage_path.endswith('.json'):
            storage = open(storage_path, 'w', encoding='utf-8')

            # Order patches by id, both for easier lookup and to
            # avoid VCs stress

            asdicts = [self.db[sid].as_dict for sid in sorted(self.db)]
            spdir = dirname(storage_path)
            for script in asdicts:
                if script.get('source'):
                    script['source'] = relpath(script['source'], spdir)

            with open(storage_path, 'w', encoding='utf-8') as storage:
                json.dump(asdicts, storage, sort_keys=True, indent=1)
        else:
            with open(storage_path, 'wb') as storage:
                pickle.dump(list(self.db.values()), storage)

        logger.debug("Done writing patches")

    def _load(self):
        db = {}
        loaded_from = {}
        for storage_path in self.storages:
            if not exists(storage_path):
                logger.debug("Storage %s does not exist, skipping", storage_path)
                continue

            logger.debug("Reading patches from %s", storage_path)
            if storage_path.endswith('.json'):
                from .patch import make_patch

                with open(storage_path, encoding='utf-8') as storage:
                    patches = [make_patch(d['ID'], d['script'], d)
                               for d in json.load(storage)]
            else:
                with open(storage_path, 'rb') as storage:
                    patches = pickle.load(storage)

            for patch in patches:
                if patch.patchid in db:
                    existing = db[patch.patchid]
                    if not patch.script:
                        existing.depends.extend(patch.depends)
                        existing.preceeds.extend(patch.preceeds)
                    elif not existing.script:
                        db[patch.patchid] = patch
                    else:
                        logger.critical("Duplicated %s: present in %s and %s",
                                        patch, loaded_from[patch.patchid], storage_path)
                        raise DuplicatedScriptError("%s already loaded!" % patch)
                else:
                    db[patch.patchid] = patch
                loaded_from[patch.patchid] = storage_path

        logger.debug("Done reading patches")
        return db

    def load(self):
        self.db = self._load()


__manager = None


def patch_manager(storage_path, overwrite=False, autosave=False):
    global __manager

    if not __manager:
        __manager = PersistentPatchManager(storage_path)
        if storage_path is not None:  # used by doctests
            if not overwrite:
                __manager.load()
            if autosave:
                import atexit
                atexit.register(__manager.save)
    return __manager
