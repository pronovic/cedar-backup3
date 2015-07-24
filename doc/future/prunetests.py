   ####################
   # Test pruneImage() 
   ####################

   def testPruneImage_001(self):
      """
      Attempt to prune an image containing no entries.
      """
      isoImage = IsoImage()
      self.failUnlessRaises(ValueError, isoImage.pruneImage, convertSize(650, UNIT_MBYTES, UNIT_BYTES))
   
   def testPruneImage_002(self):
      """
      Attempt to prune a non-empty image using a capacity for which all entries
      will fit.
      """
      self.extractTar("tree9")
      dir1 = self.buildPath([ "tree9", ])
      file1 = self.buildPath([ "tree9", "file001", ])
      file2 = self.buildPath([ "tree9", "file002", ])
      file3 = self.buildPath([ "tree9", "dir001", "file001", ])
      file4 = self.buildPath([ "tree9", "dir001", "file002", ])
      file5 = self.buildPath([ "tree9", "dir002", "file001", ])
      file6 = self.buildPath([ "tree9", "dir002", "file002", ])
      link1 = self.buildPath([ "tree9", "link001", ])
      link2 = self.buildPath([ "tree9", "link002", ])
      link3 = self.buildPath([ "tree9", "dir001", "link001", ])
      link4 = self.buildPath([ "tree9", "dir001", "link002", ])
      link5 = self.buildPath([ "tree9", "dir001", "link003", ])
      link6 = self.buildPath([ "tree9", "dir002", "link001", ])
      link7 = self.buildPath([ "tree9", "dir002", "link002", ])
      link8 = self.buildPath([ "tree9", "dir002", "link003", ])
      link9 = self.buildPath([ "tree9", "dir002", "link004", ])
      dir2 = self.buildPath([ "tree9", "dir001", "dir001", ])
      dir3 = self.buildPath([ "tree9", "dir001", "dir002", ])
      dir4 = self.buildPath([ "tree9", "dir002", "dir001", ])
      dir5 = self.buildPath([ "tree9", "dir002", "dir002", ])
      dir1graft = os.path.join("b", "tree9")
      file1graft = os.path.join("b", "tree9")
      file2graft = os.path.join("b", "tree9")
      file3graft = os.path.join("b", "tree9", "dir001")
      file4graft = os.path.join("b", "tree9", "dir001")
      file5graft = os.path.join("b", "tree9", "dir002")
      file6graft = os.path.join("b", "tree9", "dir002")
      link1graft = os.path.join("b", "tree9")
      link2graft = os.path.join("b", "tree9")
      link3graft = os.path.join("b", "tree9", "dir001", )
      link4graft = os.path.join("b", "tree9", "dir001", )
      link5graft = os.path.join("b", "tree9", "dir001", )
      link6graft = os.path.join("b", "tree9", "dir002", )
      link7graft = os.path.join("b", "tree9", "dir002", )
      link8graft = os.path.join("b", "tree9", "dir002", )
      link9graft = os.path.join("b", "tree9", "dir002", )
      dir2graft = os.path.join("b", "tree9", "dir001", "dir001", )
      dir3graft = os.path.join("b", "tree9", "dir001", "dir002", )
      dir4graft = os.path.join("b", "tree9", "dir002", "dir001", )
      dir5graft = os.path.join("b", "tree9", "dir002", "dir002", )
      isoImage = IsoImage()
      isoImage.addEntry(dir1, graftPoint="b")
      self.failUnlessEqual({ dir1:dir1graft, }, isoImage.entries)
      result = isoImage.pruneImage(convertSize(650, UNIT_MBYTES, UNIT_BYTES))  # plenty large for everything to fit
      self.failUnless(result > 0)
      self.failUnlessEqual({ file1:file1graft, file2:file2graft, file3:file3graft, file4:file4graft, 
                             file5:file5graft, file6:file6graft, link1:link1graft, link2:link2graft,
                             link3:link3graft, link4:link4graft, link5:link5graft, link6:link6graft,
                             link7:link7graft, link8:link8graft, link9:link9graft, dir2:dir2graft, 
                             dir3:dir3graft, dir4:dir4graft, dir5:dir5graft, }, isoImage.entries)
   
   def testPruneImage_003(self):
      """
      Attempt to prune a non-empty image using a capacity for which some
      entries will fit.

      This is one of those tests that may be fairly sensitive to specific
      mkisofs versions, but I don't know for sure.  A pretty-much empty image
      has around 383908 bytes of overhead.  If I set a capacity slightly larger
      than that (say 384000 bytes), some files should fit but not others.  All I
      can try to validate is that we don't get an exception and that the total
      number of included files is greater than zero.
      """
      self.extractTar("tree9")
      dir1 = self.buildPath([ "tree9", ])
      isoImage = IsoImage()
      isoImage.addEntry(dir1, None)
      self.failUnlessEqual({ dir1:os.path.basename(dir1), }, isoImage.entries)
      result = isoImage.pruneImage(384000)  # from experimentation
      self.failUnless(result > 0)
      self.failUnless(len(isoImage.entries.keys()) > 0 and len(isoImage.entries.keys()) < 19)
   
   def testPruneImage_004(self):
      """
      Attempt to prune a non-empty image using a capacity for which no entries
      will fit.

      This is one of those tests that may be fairly sensitive to specific
      mkisofs versions, but I don't know for sure.  A pretty-much empty image
      has around 381860 bytes of overhead.  I think if I use this for my
      capacity, that no files will fit and I'll throw an IOError because of
      that.  However, there's always the chance that the IOError is because not
      even the ISO header will fit, and we won't be able to differentiate those
      two cases.

      It's also important that the entries dictionary not be changed when an
      exception is thrown!
      """
      self.extractTar("tree9")
      dir1 = self.buildPath([ "tree9", ])
      isoImage = IsoImage()
      isoImage.addEntry(dir1, None)
      self.failUnlessEqual({ dir1:os.path.basename(dir1), }, isoImage.entries)
      self.failUnlessRaises(IOError, isoImage.pruneImage, 381860)  # from experimentation
   
   def testPruneImage_005(self):
      """
      Attempt to prune a non-empty image using a capacity for which not even
      the overhead will fit.

      This is one of those tests that may be fairly sensitive to specific
      mkisofs versions, but I don't know for sure.  A pretty-much empty image
      has around 381860 bytes of overhead.  I'm assuming that if I use a really
      small size (say, 10000 bytes) that I'll always get an IOError when even
      the overhead won't fit.

      It's also important that the entries dictionary not be changed when an
      exception is thrown!
      """
      self.extractTar("tree9")
      dir1 = self.buildPath([ "tree9", ])
      isoImage = IsoImage()
      isoImage.addEntry(dir1, "b")
      self.failUnlessEqual({ dir1:"b/tree9", }, isoImage.entries)
      self.failUnlessRaises(IOError, isoImage.pruneImage, 10000)  # from experimentation
      self.failUnlessEqual({ dir1:"b/tree9", }, isoImage.entries)
   
   def testWriteImage_012(self):
      """
      Attempt to write an image which has been pruned, containing several files
      and a non-empty directory, mixed graft points (results should be identical
      to test #11 because prune should be non-lossy).
      """
      self.extractTar("tree9")
      isoImage = IsoImage()
      file1 = self.buildPath([ "tree9", "file001" ])
      file2 = self.buildPath([ "tree9", "file002" ])
      dir1 = self.buildPath([ "tree9", "dir001", ])
      imagePath = self.buildPath([ "image.iso", ])
      isoImage.addEntry(file1)
      isoImage.addEntry(file2, graftPoint="other")
      isoImage.addEntry(dir1, graftPoint="base")
      isoImage.pruneImage(convertSize(650, UNIT_MBYTES, UNIT_BYTES))     # shouldn't remove any files, but will force expansion
      isoImage.writeImage(imagePath)
      mountPath = self.mountImage(imagePath)
      fsList = FilesystemList()
      fsList.addDirContents(mountPath)
      self.failUnlessEqual(13, len(fsList))
      self.failUnless(mountPath in fsList)
      self.failUnless(os.path.join(mountPath, "base", ) in fsList)
      self.failUnless(os.path.join(mountPath, "other", ) in fsList)
      self.failUnless(os.path.join(mountPath, "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "other", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "link003", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", "dir002", ) in fsList)

   def testWriteImage_014(self):
      """
      Attempt to write an image which has been pruned, containing a deeply-
      nested directory (results should be identical to test #13 because prune
      should be non-lossy).
      """
      self.extractTar("tree9")
      isoImage = IsoImage()
      dir1 = self.buildPath([ "tree9", ])
      imagePath = self.buildPath([ "image.iso", ])
      isoImage.addEntry(dir1, graftPoint="something")
      isoImage.pruneImage(convertSize(650, UNIT_MBYTES, UNIT_BYTES))     # shouldn't remove any files, but will force expansion
      isoImage.writeImage(imagePath)
      mountPath = self.mountImage(imagePath)
      fsList = FilesystemList()
      fsList.addDirContents(mountPath)
      self.failUnlessEqual(24, len(fsList))
      self.failUnless(mountPath in fsList)
      self.failUnless(os.path.join(mountPath, "something", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "link003", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir001", "dir002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "link003", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "link004", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "tree9", "dir002", "dir002", ) in fsList)

   def testWriteImage_025(self):
      """
      Attempt to write an image which has been pruned, containing several files
      and a non-empty directory, mixed graft points, contentsOnly=True (results
      should be identical to test #24 because prune should be non-lossy).
      """
      self.extractTar("tree9")
      isoImage = IsoImage()
      file1 = self.buildPath([ "tree9", "file001" ])
      file2 = self.buildPath([ "tree9", "file002" ])
      dir1 = self.buildPath([ "tree9", "dir001", ])
      imagePath = self.buildPath([ "image.iso", ])
      isoImage.addEntry(file1, contentsOnly=True)
      isoImage.addEntry(file2, graftPoint="other", contentsOnly=True)
      isoImage.addEntry(dir1, graftPoint="base", contentsOnly=True)
      isoImage.pruneImage(convertSize(650, UNIT_MBYTES, UNIT_BYTES))     # shouldn't remove any files, but will force expansion
      isoImage.writeImage(imagePath)
      mountPath = self.mountImage(imagePath)
      fsList = FilesystemList()
      fsList.addDirContents(mountPath)
      self.failUnlessEqual(12, len(fsList))
      self.failUnless(mountPath in fsList)
      self.failUnless(os.path.join(mountPath, "base", ) in fsList)
      self.failUnless(os.path.join(mountPath, "other", ) in fsList)
      self.failUnless(os.path.join(mountPath, "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "other", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "link003", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "base", "dir002", ) in fsList)

   def testWriteImage_027(self):
      """
      Attempt to write an image which has been pruned, containing a deeply-
      nested directory, contentsOnly=True (results should be identical to test
      #26 because prune should be non-lossy).
      """
      self.extractTar("tree9")
      isoImage = IsoImage()
      dir1 = self.buildPath([ "tree9", ])
      imagePath = self.buildPath([ "image.iso", ])
      isoImage.addEntry(dir1, graftPoint="something", contentsOnly=True)
      isoImage.pruneImage(convertSize(650, UNIT_MBYTES, UNIT_BYTES))     # shouldn't remove any files, but will force expansion
      isoImage.writeImage(imagePath)
      mountPath = self.mountImage(imagePath)
      fsList = FilesystemList()
      fsList.addDirContents(mountPath)
      self.failUnlessEqual(23, len(fsList))
      self.failUnless(mountPath in fsList)
      self.failUnless(os.path.join(mountPath, "something", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "link003", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir001", "dir002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "file001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "file002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "link001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "link002", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "link003", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "link004", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "dir001", ) in fsList)
      self.failUnless(os.path.join(mountPath, "something", "dir002", "dir002", ) in fsList)


   def testUtilityMethods_023(self):
      """
      Test _calculateSizes with an empty entries dictionary.
      """
      entries = {}
      (table, total) = IsoImage._calculateSizes(entries)
      self.failUnlessEqual({}, table)
      self.failUnlessEqual(0, total)

   def testUtilityMethods_024(self):
      """
      Test _calculateSizes with an entries dictionary containing only a single file.
      """
      entries = {}
      self.extractTar("tree9")
      file1 = self.buildPath(["tree9", "file001", ])
      entries[file1] = None
      (table, total) = IsoImage._calculateSizes(entries)
      self.failUnlessEqual({ file1:(file1,155), }, table)
      self.failUnlessEqual(155, total)
      
   def testUtilityMethods_025(self):
      """
      Test _calculateSizes with an entries dictionary containing multiple files.
      """
      entries = {}
      self.extractTar("tree9")
      file1 = self.buildPath(["tree9", "file001", ])
      file2 = self.buildPath(["tree9", "file002", ])
      file3 = self.buildPath(["tree9", "dir001", "file001", ])
      entries[file1] = None
      entries[file2] = None
      entries[file3] = None
      (table, total) = IsoImage._calculateSizes(entries)
      self.failUnlessEqual({ file1:(file1,155), file2:(file2,242), file3:(file3,243), }, table)
      self.failUnlessEqual(640, total)

   def testUtilityMethods_026(self):
      """
      Test _calculateSizes with an entries dictionary containing files,
      directories, links and invalid items.
      """
      entries = {}
      self.extractTar("tree9")
      file1 = self.buildPath(["tree9", "file001", ])
      file2 = self.buildPath(["tree9", "file002", ])
      file3 = self.buildPath(["tree9", "dir001", "file001", ])
      file4 = self.buildPath(["tree9", INVALID_FILE, ])
      dir1 = self.buildPath(["tree9", "dir001", ])
      link1 = self.buildPath(["tree9", "link001", ])
      entries[file1] = None
      entries[file2] = None
      entries[file3] = None
      entries[file4] = None
      entries[dir1] = None
      entries[link1] = None
      (table, total) = IsoImage._calculateSizes(entries)
      self.failUnlessEqual({ file1:(file1,155), file2:(file2,242), file3:(file3,243), dir1:(dir1,0), link1:(link1,0)}, table)
      self.failUnlessEqual(640, total)


   def testUtilityMethods_030(self):
      """
      Test _expandEntries with an empty entries dictionary.
      """
      entries = {}
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({}, result)

   def testUtilityMethods_031(self):
      """
      Test _expandEntries with an entries dictionary containing only a single file.
      """
      entries = {}
      self.extractTar("tree9")
      file1 = self.buildPath(["tree9", "file001", ])
      entries[file1] = None
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({ file1:None, }, result)

   def testUtilityMethods_032(self):
      """
      Test _expandEntries with an entries dictionary containing only files.
      """
      entries = {}
      self.extractTar("tree9")
      file1 = self.buildPath(["tree9", "file001", ])
      file2 = self.buildPath(["tree9", "file002", ])
      entries[file1] = None
      entries[file2] = "whatever"
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({ file1:None, file2:"whatever", }, result)

   def testUtilityMethods_033(self):
      """
      Test _expandEntries with an entries dictionary containing only a single empty directory.
      """
      entries = {}
      self.extractTar("tree9")
      dir1 = self.buildPath(["tree9", "dir002", "dir001", ])
      dir1graft = os.path.join("something", "dir001") 
      entries[dir1] = "something"
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({dir1:dir1graft, }, result)

   def testUtilityMethods_034(self):
      """
      Test _expandEntries with an entries dictionary containing only a single non-empty directory.
      """
      entries = {}
      self.extractTar("tree9")
      dir1 = self.buildPath(["tree9", "dir001", ])
      file1 = self.buildPath(["tree9", "dir001", "file001", ])
      file2 = self.buildPath(["tree9", "dir001", "file002", ])
      link1 = self.buildPath(["tree9", "dir001", "link001", ])
      link2 = self.buildPath(["tree9", "dir001", "link002", ])
      link3 = self.buildPath(["tree9", "dir001", "link003", ])
      dir2 = self.buildPath(["tree9", "dir001", "dir001", ])
      dir3 = self.buildPath(["tree9", "dir001", "dir002", ])
      dir1graft = os.path.join("something", "dir001")
      dir2graft = os.path.join("something", "dir001", "dir001", )
      dir3graft = os.path.join("something", "dir001", "dir002", )
      entries[dir1] = "something/dir001"
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({ file1:dir1graft, file2:dir1graft, 
                             link1:dir1graft, link2:dir1graft, link3:dir1graft, 
                             dir2:dir2graft, dir3:dir3graft, }, result)

   def testUtilityMethods_035(self):
      """
      Test _expandEntries with an entries dictionary containing only directories.
      """
      entries = {}
      self.extractTar("tree9")
      dir1 = self.buildPath(["tree9", "dir001", ])
      dir2 = self.buildPath(["tree9", "dir002", ])
      file1 = self.buildPath(["tree9", "dir001", "file001", ])
      file2 = self.buildPath(["tree9", "dir001", "file002", ])
      file3 = self.buildPath(["tree9", "dir002", "file001", ])
      file4 = self.buildPath(["tree9", "dir002", "file002", ])
      link1 = self.buildPath(["tree9", "dir001", "link001", ])
      link2 = self.buildPath(["tree9", "dir001", "link002", ])
      link3 = self.buildPath(["tree9", "dir001", "link003", ])
      link4 = self.buildPath(["tree9", "dir002", "link001", ])
      link5 = self.buildPath(["tree9", "dir002", "link002", ])
      link6 = self.buildPath(["tree9", "dir002", "link003", ])
      link7 = self.buildPath(["tree9", "dir002", "link004", ])
      dir3 = self.buildPath(["tree9", "dir001", "dir001", ])
      dir4 = self.buildPath(["tree9", "dir001", "dir002", ])
      dir5 = self.buildPath(["tree9", "dir002", "dir001", ])
      dir6 = self.buildPath(["tree9", "dir002", "dir002", ])
      dir1graft = os.path.join("something", "dir001")
      dir2graft = os.path.join("whatever", "dir002")
      dir3graft = os.path.join("something", "dir001", "dir001", )
      dir4graft = os.path.join("something", "dir001", "dir002", )
      dir5graft = os.path.join("whatever", "dir002", "dir001", )
      dir6graft = os.path.join("whatever", "dir002", "dir002", )
      entries[dir1] = "something/dir001"
      entries[dir2] = "whatever/dir002"
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({ file1:dir1graft, file2:dir1graft, file3:dir2graft, file4:dir2graft, 
                             link1:dir1graft, link2:dir1graft, link3:dir1graft, link4:dir2graft,
                             link5:dir2graft, link6:dir2graft, link7:dir2graft, 
                             dir3:dir3graft, dir4:dir4graft, dir5:dir5graft, dir6:dir6graft, }, result)

   def testUtilityMethods_036(self):
      """
      Test _expandEntries with an entries dictionary containing files and directories.
      """
      entries = {}
      self.extractTar("tree9")
      dir1 = self.buildPath(["tree9", "dir001", ])
      dir2 = self.buildPath(["tree9", "dir002", ])
      file1 = self.buildPath(["tree9", "dir001", "file001", ])
      file2 = self.buildPath(["tree9", "dir001", "file002", ])
      file3 = self.buildPath(["tree9", "dir002", "file001", ])
      file4 = self.buildPath(["tree9", "dir002", "file002", ])
      file5 = self.buildPath(["tree9", "file001", ])
      file6 = self.buildPath(["tree9", "file002", ])
      link1 = self.buildPath(["tree9", "dir001", "link001", ])
      link2 = self.buildPath(["tree9", "dir001", "link002", ])
      link3 = self.buildPath(["tree9", "dir001", "link003", ])
      link4 = self.buildPath(["tree9", "dir002", "link001", ])
      link5 = self.buildPath(["tree9", "dir002", "link002", ])
      link6 = self.buildPath(["tree9", "dir002", "link003", ])
      link7 = self.buildPath(["tree9", "dir002", "link004", ])
      dir3 = self.buildPath(["tree9", "dir001", "dir001", ])
      dir4 = self.buildPath(["tree9", "dir001", "dir002", ])
      dir5 = self.buildPath(["tree9", "dir002", "dir001", ])
      dir6 = self.buildPath(["tree9", "dir002", "dir002", ])
      file1graft = os.path.join("something", "dir001")
      file2graft = os.path.join("something", "dir001")
      file3graft = None
      file4graft = None
      file5graft = None
      file6graft = os.path.join("three")
      link1graft = os.path.join("something", "dir001")
      link2graft = os.path.join("something", "dir001")
      link3graft = os.path.join("something", "dir001")
      link4graft = None
      link5graft = None
      link6graft = None
      link7graft = None
      dir3graft = os.path.join("something", "dir001", "dir001", )
      dir4graft = os.path.join("something", "dir001", "dir002", )
      dir5graft = "dir001"
      dir6graft = "dir002"
      entries[dir1] = "something/dir001"
      entries[dir2] = None
      entries[file5] = None
      entries[file6] = "three"
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({ file1:file1graft, file2:file2graft, file3:file3graft, file4:file4graft,
                             file5:file5graft, file6:file6graft, link1:link1graft, link2:link2graft,
                             link3:link3graft, link4:link4graft, link5:link5graft, link6:link6graft,
                             link7:link7graft, dir3:dir3graft, dir4:dir4graft, dir5:dir5graft, dir6:dir6graft, }, result)

   def testUtilityMethods_037(self):
      """
      Test _expandEntries with a deeply-nested entries dictionary.
      """
      entries = {}
      self.extractTar("tree9")
      dir1 = self.buildPath(["tree9", ])
      file1 = self.buildPath(["tree9", "dir001", "file001", ])
      file2 = self.buildPath(["tree9", "dir001", "file002", ])
      file3 = self.buildPath(["tree9", "dir002", "file001", ])
      file4 = self.buildPath(["tree9", "dir002", "file002", ])
      file5 = self.buildPath(["tree9", "file001", ])
      file6 = self.buildPath(["tree9", "file002", ])
      link1 = self.buildPath(["tree9", "dir001", "link001", ])
      link2 = self.buildPath(["tree9", "dir001", "link002", ])
      link3 = self.buildPath(["tree9", "dir001", "link003", ])
      link4 = self.buildPath(["tree9", "dir002", "link001", ])
      link5 = self.buildPath(["tree9", "dir002", "link002", ])
      link6 = self.buildPath(["tree9", "dir002", "link003", ])
      link7 = self.buildPath(["tree9", "dir002", "link004", ])
      link8 = self.buildPath(["tree9", "link001", ])
      link9 = self.buildPath(["tree9", "link002", ])
      dir2 = self.buildPath(["tree9", "dir001", "dir001", ])
      dir3 = self.buildPath(["tree9", "dir001", "dir002", ])
      dir4 = self.buildPath(["tree9", "dir002", "dir001", ])
      dir5 = self.buildPath(["tree9", "dir002", "dir002", ])
      file1graft = os.path.join("bogus", "tree9", "dir001")
      file2graft = os.path.join("bogus", "tree9", "dir001")
      file3graft = os.path.join("bogus", "tree9", "dir002")
      file4graft = os.path.join("bogus", "tree9", "dir002")
      file5graft = os.path.join("bogus", "tree9")
      file6graft = os.path.join("bogus", "tree9")
      link1graft = os.path.join("bogus", "tree9", "dir001")
      link2graft = os.path.join("bogus", "tree9", "dir001")
      link3graft = os.path.join("bogus", "tree9", "dir001")
      link4graft = os.path.join("bogus", "tree9", "dir002")
      link5graft = os.path.join("bogus", "tree9", "dir002")
      link6graft = os.path.join("bogus", "tree9", "dir002")
      link7graft = os.path.join("bogus", "tree9", "dir002")
      link8graft = os.path.join("bogus", "tree9", )
      link9graft = os.path.join("bogus", "tree9", )
      dir2graft = os.path.join("bogus", "tree9", "dir001", "dir001", )
      dir3graft = os.path.join("bogus", "tree9", "dir001", "dir002", )
      dir4graft = os.path.join("bogus", "tree9", "dir002", "dir001", )
      dir5graft = os.path.join("bogus", "tree9", "dir002", "dir002", )
      entries[dir1] = "bogus/tree9"
      result = IsoImage._expandEntries(entries)
      self.failUnlessEqual({ file1:file1graft, file2:file2graft, file3:file3graft, file4:file4graft,
                             file5:file5graft, file6:file6graft, link1:link1graft, link2:link2graft,
                             link3:link3graft, link4:link4graft, link5:link5graft, link6:link6graft,
                             link7:link7graft, link8:link8graft, link9:link9graft, dir2:dir2graft,
                             dir3:dir3graft, dir4:dir4graft, dir5:dir5graft, }, result)


   def testUtilityMethods_026(self):
      """
      Test _calculateSizes with an entries dictionary containing files,
      directories, links and invalid items.
      """
      entries = {}
      self.extractTar("tree9")
      file1 = self.buildPath(["tree9", "file001", ])
      file2 = self.buildPath(["tree9", "file002", ])
      file3 = self.buildPath(["tree9", "dir001", "file001", ])
      file4 = self.buildPath(["tree9", INVALID_FILE, ])
      dir1 = self.buildPath(["tree9", "dir001", ])
      link1 = self.buildPath(["tree9", "link001", ])
      entries[file1] = None
      entries[file2] = None
      entries[file3] = None
      entries[file4] = None
      entries[dir1] = None
      entries[link1] = None
      (table, total) = IsoImage._calculateSizes(entries)
      self.failUnlessEqual({ file1:(file1,155), file2:(file2,242), file3:(file3,243), dir1:(dir1,0), link1:(link1,0)}, table)
      self.failUnlessEqual(640, total)

   def testUtilityMethods_027(self):
      """
      Test _buildEntries with an empty entries dictionary and empty items list.
      """
      entries = {}
      items = []
      result = IsoImage._buildEntries(entries, items)
      self.failUnlessEqual({}, result)

   def testUtilityMethods_028(self):
      """
      Test _buildEntries with a valid entries dictionary and items list.
      """
      entries = { "a":1, "b":2, "c":3, "d":4, "e":5, "f":6, }
      items = [ "a", "c", "e", ]
      result = IsoImage._buildEntries(entries, items)
      self.failUnlessEqual({ "a":1, "c":3, "e":5, }, result)

   def testUtilityMethods_029(self):
      """
      Test _buildEntries with an items list containing a key not in the entries dictionary.
      """
      entries = { "a":1, "b":2, "c":3, "d":4, "e":5, "f":6, }
      items = [ "a", "c", "e", "z", ]
      self.failUnlessRaises(KeyError, IsoImage._buildEntries, entries, items)
