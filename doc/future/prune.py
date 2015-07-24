   ######################
   # Prune functionality
   ######################

   def pruneImage(self, capacity):
      """
      Prunes the image to fit a certain capacity, in bytes.

      The contents of the image will be pruned in an attempt to fit the image
      into the indicated capacity.  The pruning process is iterative and might
      take a number of attempts to get right because we can't always be sure
      what overhead the ISO protocol will add.  We'll only try a certain number
      of times before giving up and raising an C{IOError} exception.

      @note: Pruning an image has the effect of expanding any directory to its
      list of composite files internally.  

      @note: This process is destructive.  Once you prune an image, you can't
      get it back in its original form without rebuilding it from scratch.
      However, the object will be unchanged unless this method call returns
      successfully.

      @param capacity: Capacity to prune to
      @type capacity: Integer capacity, in bytes

      @return: Estimated size of the image, in bytes, as from L{getEstimatedSize}.

      @raise IOError: If we can't prune to fit the image into the capacity.
      @raise ValueError: If there are no filesystem entries in the image
      """
      if len(self.entries.keys()) == 0:
         raise ValueError("Image does not contain any entries.")
      entries = self._pruneImage(capacity)
      self.entries = entries
      return self.getEstimatedSize()

   def _pruneImage(self, capacity):
      """
      Prunes the image to fit a certain capacity, in bytes.

      This is an internal method.  It mainly exists so we can adequately
      document the pruning procedure without burdening external callers with
      details about exactly how it's done.

      To be successful, we have to build an entries dictionary such that the
      resulting ISO image uses C{capacity} or fewer bytes.  We determine a
      target overall file size, use a knapsack algorithm to hit that target
      size, and then check whether the resulting image would fit in our
      capacity.  If it would fit, then we build a new entries dictionary and
      return it.  Otherwise we try a few more times, giving up after four
      attempts.

      The trick is figuring out how to determine the target overall file size,
      by which we mean the target size among the files represented by the list
      of entries.  This size doesn't map directly to the capacity, because it
      doesn't take into account overhead related to the ISO image or to storing
      directories and links (which look "empty" on the filesystem).

      The first step is to establish a relationship between the size of the
      files in the image and the size of the image itself.  The size of the
      image minus the size of the files gives us a value for approximate
      overhead required to create the image.  Assuming that the overhead won't
      get any larger if the number of entries shrinks, our new target overall
      file size is the capacity minus the overhead.  Initially, we try to
      generate our list of entries using the original target capacity.  If that
      doesn't work, we make a few additional passes, subtracting off a bit more
      capacity each time.

      We always consider it to be an error if we are unable to fit any files
      into the image.  That's important to notice, because if no files fit,
      that accidentally could look like success to us (the image would
      certainly be small enough).

      @param capacity: Capacity to prune to
      @type capacity: Integer capacity, in bytes

      @return: Pruned entries dictionary safe to apply to self.entries
      @raise IOError: If we can't prune to fit the image into the capacity.
      """
      expanded = self._expandEntries(self.entries) 
      (sizeMap, fileSize) = IsoImage._calculateSizes(expanded)
      estimatedSize = self._getEstimatedSize(self.entries)
      overhead = estimatedSize - fileSize
      if overhead > capacity:
         raise IOError("Required overhead (%.0f) exceeds available capacity (%.0f)." % (overhead, float(capacity)))
      for factor in [ 1.0, 0.98, 0.95, 0.90 ]:
         targetSize = (capacity - overhead) * factor
         (items, used) = worstFit(sizeMap, targetSize)
         if len(items) == 0 or used == 0:
            raise IOError("Unable to fit any entries into available capacity.")
         prunedEntries = IsoImage._buildEntries(expanded, items)
         estimatedSize = self._getEstimatedSize(prunedEntries)
         if(estimatedSize <= capacity):
            return prunedEntries
      raise IOError("Unable to prune image to fit the capacity after four tries.")

   @staticmethod
   def _calculateSizes(entries):
      """
      Calculates sizes for files in an entries dictionary.

      The resulting map contains true sizes for each file in the list of
      entries, and the total is the sum of all of these sizes.  The map also
      contains zero size for each link and directory in the original list of
      entries.  This way, the process of calculating sizes doesn't lose any
      information (it's up to the caller to pass in an entries list that
      contains only things they care about).  In any case, an entry which
      doesn't exist on disk is completely ignored.

      @param entries: An entries map (expanded via L{_expandEntries})

      @return: Tuple (map, total) where map is suitable for passing to a knapsack function.
      """
      table = { }
      total = 0
      for entry in entries:
         if os.path.exists(entry):
            if os.path.isfile(entry) and not os.path.islink(entry):
               size = float(os.stat(entry).st_size)
               table[entry] = (entry, size)
               total += size
            else:
               table[entry] = (entry, 0)
      return (table, total)

   @staticmethod
   def _buildEntries(entries, items):
      """
      Builds an entries dictionary.
      
      The result is basically the intersection of the passed-in entries
      dictionary with the keys that are in the list.  The passed-in entries
      dictionary will not be modified.  The items list is assumed to be a
      subset of the list of keys in the entries dictionary and you'll get a
      C{KeyError} if that's not true.

      @param entries: Entries dictionary to work from
      @param items: List of items to be used as keys into the dictionary

      @return: New entries dictionary that contains only the keys in the list
      @raise KeyError: If the items doesn't match up properly with entries.
      """
      newEntries = { }
      for i in items:
         newEntries[i] = entries[i]
      return newEntries

   @staticmethod
   def _expandEntries(entries):
      """
      Expands entries in an image to include only files.

      Most of the time, we will add only directories to an image, with an
      occassional file here and there.  However, we need to get at the files in
      the each directory in order to prune to fit a particular capacity.  So,
      this function goes through the the various entries and expands every
      directory it finds.  The result is an "equivalent" entries dictionary
      that verbosely includes every file and link that would have been included
      originally, along with its associated graft point (if any).  

      There is one trick: we can't associate the same graft point with a file
      as with its parent directory, since this would lose information (such as
      the directory the file was in, especially if it was deeply nested).  We
      sometimes need to tack the name of a directory onto the end of the graft
      point so the result will be equivalent.

      Here's an example: if directory C{/opt/ken/dir1} had graft point
      C{/base}, then the directory would become C{/base/dir1} in the image and
      individual files might be C{/base/dir1/file1}, C{/base/dir1/file2}, etc.
      Because of our specialized graft-point handling for directories, this
      works in the simple case.  However, once you work your way into nested
      directories, it breaks down.  In order to get C{/base/dir1/dir2/file1},
      we need to recognize that the prefix is really C{dir2} and tack that onto
      the graft point.  

      Besides this, there are a few other hoops we have to jump through.  In
      particular, we need to include soft links in the image, but
      non-recursively (i.e. we don't want to traverse soft links to
      directories).  Also, while we don't normally want bare directories in the
      image (because the files in those directories will already have been
      added) we need to be careful not to lose empty directories, which will
      get pruned by a simplistic algorithm simply because they don't contain
      any indexed files.  The bare directories are added with a graft point
      including their own name, to force C{mkisofs} to create them.

      @note: Behavior of this function is probably UN*X-specific.

      @return: Expanded entries dictionary.
      """
      newEntries = { }
      for entry in entries:
         if os.path.isfile(entry):
            newEntries[entry] = entries[entry]
         elif os.path.isdir(entry):
            fsList = FilesystemList()
            fsList.addDirContents(entry)
            for item in fsList:
               if os.path.islink(item) or os.path.isfile(item):
                  if entries[entry] is None:
                     newEntries[item] = None
                  else:
                     subdir = os.path.dirname(item.replace(entry, "", 1))
                     graft = os.path.join(entries[entry].strip(os.sep), subdir.strip(os.sep))
                     newEntries[item] = graft.strip(os.sep)
               elif os.path.os.path.isdir(item) and os.listdir(item) == []:
                  if entries[entry] is None:
                     newEntries[item] = os.path.basename(item)
                  else:
                     subdir = os.path.dirname(item.replace(entry, "", 1))
                     graft = os.path.join(entries[entry].strip(os.sep), subdir.strip(os.sep), os.path.basename(item))
                     newEntries[item] = graft.strip(os.sep)
      return newEntries

