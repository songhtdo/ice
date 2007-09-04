#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2007 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import os, sys, shutil, fnmatch, re, glob

#
# Program usage.
#
def usage():
    print "Usage: " + sys.argv[0] + " [options]"
    print
    print "Options:"
    print "-h    Show this message."
    print "-v    Be verbose."

#
# Find files matching a pattern.
#
def find(path, patt):
    result = [ ]
    files = os.listdir(path)
    for x in files:
        fullpath = os.path.join(path, x);
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            result.extend(find(fullpath, patt))
        elif fnmatch.fnmatch(x, patt):
            result.append(fullpath)
    return result

#
# Comment out rules in a Makefile.
#
def fixMakefile(file, target):
    origfile = file + ".orig"
    os.rename(file, origfile)
    oldMakefile = open(origfile, "r")
    newMakefile = open(file, "w")
    origLines = oldMakefile.readlines()

    doComment = 0
    doCheck = 0
    newLines = []
    for x in origLines:
        #
        # If the rule contains the target string, then
        # comment out this rule.
        #
        if not x.startswith("\t") and x.find(target) != -1 and x.find(target + ".o") == -1:
            doComment = 1
        #
        # If the line starts with "clean::", then check
        # the following lines and comment out any that
        # contain the target string.
        #
        elif x.startswith("clean::"):
            doCheck = 1
        #
        # Stop when we encounter an empty line.
        #
        elif len(x.strip()) == 0:
            doComment = 0
            doCheck = 0

        if doComment or (doCheck and x.find(target) != -1):
            x = "#" + x
        newLines.append(x)

    newMakefile.writelines(newLines)
    newMakefile.close()
    oldMakefile.close()
    os.remove(origfile)

#
# Remove lines containing a keyword from a file.
#
def editFile(file, target):
    origfile = file + ".orig"
    os.rename(file, origfile)
    oldFile = open(origfile, "r")
    newFile = open(file, "w")
    origLines = oldFile.readlines()

    newLines = []
    for x in origLines:
        if x.find(target) == -1:
            newLines.append(x)

    newFile.writelines(newLines)
    newFile.close()
    oldFile.close()
    os.remove(origfile)

#
# Comment out rules in VC project.
#
def fixProject(file, target):
    origfile = file + ".orig"
    os.rename(file, origfile)
    oldProject = open(origfile, "r")
    newProject = open(file, "w")
    origLines = oldProject.readlines()

    #
    # Find a Source File declaration containing SOURCE=<target>
    # and comment out the entire declaration.
    #
    expr = re.compile("SOURCE=.*" + target.replace(".", "\\.") + ".*")
    inSource = 0
    doComment = 0
    newLines = []
    source = []
    for x in origLines:
        if x.startswith("# Begin Source File"):
            inSource = 1

        if inSource:
            if not doComment and expr.match(x) != None:
                doComment = 1
            source.append(x)
        else:
            newLines.append(x)

        if x.startswith("# End Source File"):
            inSource = 0
            for s in source:
                if doComment:
                    newLines.append('#xxx#' + s)
                else:
                    newLines.append(s)
            doComment = 0
            source = []

    newProject.writelines(newLines)
    newProject.close()
    oldProject.close()
    os.remove(origfile)

#
# Comment out implicit parser/scanner rules in config/Make.rules.
#
def fixMakeRules(file):
    origfile = file + ".orig"
    os.rename(file, origfile)
    oldFile = open(origfile, "r")
    newFile = open(file, "w")
    origLines = oldFile.readlines()

    doComment = 0
    newLines = []
    for x in origLines:
        if x.find("%.y") != -1 or x.find("%.l") != -1:
            doComment = 1
        #
        # Stop when we encounter an empty line.
        #
        elif len(x.strip()) == 0:
            doComment = 0

        if doComment:
            x = "#" + x
        newLines.append(x)

    newFile.writelines(newLines)
    newFile.close()
    oldFile.close()
    os.remove(origfile)

#
# Fix version in README, INSTALL files
#
def fixVersion(files, version, mmversion):

    for file in files:
        origfile = file + ".orig"
        os.rename(file, origfile)
        oldFile = open(origfile, "r")
        newFile = open(file, "w")
        line = oldFile.read();
        line = re.sub("@ver@", version, line)
        line = re.sub("@mmver@", mmversion, line)
        newFile.write(line)
        newFile.close()
        oldFile.close()
        os.remove(origfile)

#
# Check arguments
#
verbose = 0
for x in sys.argv[1:]:
    if x == "-h":
        usage()
        sys.exit(0)
    elif x == "-v":
        verbose = 1
    elif x.startswith("-"):
        print sys.argv[0] + ": unknown option `" + x + "'"
        print
        usage()
        sys.exit(1)

if os.path.exists("../.git"):
    print "ERROR: Unable to run in repository! Exiting..."
    sys.exit(1)
    
#
# Remove any existing "dist" directory and create a new one.
#
distdir = "dist"
if os.path.exists(distdir):
    shutil.rmtree(distdir)
os.mkdir(distdir)

if verbose:
    quiet = "v"
else:
    quiet = ""

#
# Get Ice version.
#
config = open(os.path.join("include", "IceUtil", "Config.h"), "r")
version = re.search("ICE_STRING_VERSION \"([0-9\.b]*)\"", config.read()).group(1)
mmversion = re.search("([0-9]+\.[0-9b]+)[\.0-9]*", version).group(1)

print "Creating Ice-rpmbuild..."
rpmbuildver = os.path.join("dist", "Ice-rpmbuild-" + version)
fixVersion(find(os.path.join("install", "rpm"), "icegridregistry.*"), version, mmversion)
fixVersion(find(os.path.join("install", "rpm"), "icegridnode.*"), version, mmversion)
fixVersion(find(os.path.join("install", "rpm"), "glacier2router.*"), version, mmversion)
fixVersion(find(os.path.join("install", "rpm"), "README.RPM"), version, mmversion)
fixVersion(find(os.path.join("install", "unix"), "THIRD_PARTY_LICENSE.Linux"), version, mmversion)
fixVersion(find(os.path.join("install", "unix"), "README.Linux-RPM"), version, mmversion)
fixVersion(find(os.path.join("install", "unix"), "SOURCES.Linux"), version, mmversion)

if os.system("tar c" + quiet + "f " + rpmbuildver + ".tar " +
        "-C .. `[ -e RELEASE_NOTES.txt ] && echo ""RELEASE_NOTES.txt""` " +
        "-C cpp/install -C rpm {icegridregistry,icegridnode,glacier2router}.{conf,suse,redhat} README.RPM " +
        "-C ../unix THIRD_PARTY_LICENSE.Linux README.Linux-RPM SOURCES.Linux " +
        "-C ../thirdparty/php ice.ini"):
    print >> sys.stderr, "ERROR: Archiving failed"
    sys.exit(1)
   
if os.system("gzip -9 " + rpmbuildver + ".tar"):
    print >> sys.stderr, "ERROR: Archiving failed"
    sys.exit(1)


#
# Create archives.
#
print "Creating distribution..."
icever = "Ice-" + version

print "Creating exclusion file..."
filesToRemove = [ \
    "makedist.py", \
    "makebindist.py", \
    "iceemakedist.py", \
    "RPMTools.py", \
    "fixCopyright.py", \
    "fixVersion.py", \
    "icee.dsw", \
    "icee.dsp", \
    "allDemos.py", \
    os.path.join("config", "makegitignore.py"), \
    os.path.join("src", "icecpp", "icecppe.dsp"), \
    os.path.join("src", "IceUtil", "iceutile.dsp"), \
    os.path.join("src", "Slice", "slicee.dsp"), \
    "dist", \
    "install", \
    os.path.join("src", "slice2cppe"), \
    os.path.join("src", "slice2javae"), \
    os.path.join("exclusions")
    ]

filesToRemove.extend(find(".", ".gitignore"))
filesToRemove.extend(find(".", "expect.py"))

exclusionFile = open("exclusions", "w")
for x in filesToRemove:
    exclusionFile.write("%s\n" % x)
exclusionFile.close()
os.mkdir(os.path.join("dist", icever))
if os.system("tar c" + quiet + " -X exclusions . | ( cd " + os.path.join("dist", icever) + " && tar xf - )"):
    print >> sys.stderr, "ERROR: demo script archive caused errors"
    sys.exit(1)
os.remove("exclusions")
os.chdir("dist")

if os.system("chmod -R u+rw,go+r-w %s " % icever):
    print >> sys.stderr, "ERROR: unable to set directory permissions"
    sys.exit(1)

#
# Printing warnings here instead of exiting because these probably
# are not errors per-se but may reflect an unnecessary operation.
#
if os.system("find %s \\( -name \"*.h\" -or -name \"*.cpp\" -or -name \"*.ice\" \\) -exec chmod a-x {} \\;" % icever):
    print >> sys.stderr, "WARNING: find returned non-zero result"
if os.system("find %s \\( -name \"README*\" -or -name \"INSTALL*\" \\) -exec chmod a-x {} \\;" % icever):
    print >> sys.stderr, "WARNING: find returned non-zero result"
if os.system("find %s \\( -name \"*.xml\" -or -name \"*.mc\" \\) -exec chmod a-x {} \\;" % icever):
    print >> sys.stderr, "WARNING: find returned non-zero result"
if os.system("find %s \\( -name \"Makefile\" -or -name \"*.dsp\" \\) -exec chmod a-x {} \\;" % icever):
    print >> sys.stderr, "WARNING: find returned non-zero result"
if os.system("find %s -type d -exec chmod a+x {} \\;" % icever):
    print >> sys.stderr, "WARNING: find returned non-zero result"
if os.system("find %s -perm +111 -exec chmod a+x {} \\;" % icever):
    print >> sys.stderr, "WARNING: find returned non-zero result"

print "Fixing version in various files..."
fixVersion(find(icever, "README*"), version, mmversion)
fixVersion(find(icever, "INSTALL*"), version, mmversion)
fixVersion(find(os.path.join(icever, "config"), "glacier2router.cfg"), version, mmversion)
fixVersion(find(os.path.join(icever, "config"), "icegridregistry.cfg"), version, mmversion)

#
# Generate bison files.
#
print "Generating bison files..."
cwd = os.getcwd()
grammars = find(icever, "*.y")
for x in grammars:
    #
    # Change to the directory containing the file.
    #
    (dir,file) = os.path.split(x)
    os.chdir(dir)
    (base,ext) = os.path.splitext(file)
    #
    # Run gmake to create the output files.
    #
    if verbose:
        quiet = ""
    else:
        quiet = "-s"
    result = 0
    if file == "cexp.y":
        result = os.system("gmake " + quiet + " cexp.c")
    else:
        result = os.system("gmake " + quiet + " " + base + ".cpp")
    if result:
        print 
    #
    # Edit the Makefile to comment out the grammar rules.
    #
    fixMakefile("Makefile", base)
    fixMakefile("Makefile.mak", base)

    #
    # Edit the project file(s) to comment out the grammar rules.
    #
    for p in glob.glob("*.dsp"):
        fixProject(p, file)
    os.chdir(cwd)

#
# Generate flex files.
#
print "Generating flex files..."
scanners = find(icever, "*.l")
for x in scanners:
    #
    # Change to the directory containing the file.
    #
    (dir,file) = os.path.split(x)
    os.chdir(dir)
    (base,ext) = os.path.splitext(file)
    #
    # Run gmake to create the output files.
    #
    if verbose:
        quiet = ""
    else:
        quiet = "-s"
    if os.system("gmake " + quiet + " " + base + ".cpp"):
        print>>sys.stderr, "Generating flex files failed."
        sys.exit(1)
    #
    # Edit the Makefile to comment out the flex rules.
    #
    fixMakefile("Makefile", base)
    fixMakefile("Makefile.mak", base)

    #
    # Edit the project file(s) to comment out the flex rules.
    #
    for p in glob.glob("*.dsp"):
        fixProject(p, file)
    os.chdir(cwd)

if verbose:
    quiet = "v"
else:
    quiet = ""

#
# Comment out the implicit parser and scanner rules in
# config/Make.rules.
#
print "Fixing makefiles..."
fixMakeRules(os.path.join(icever, "config", "Make.rules"))

if os.system("tar c" + quiet + "f %s.tar %s" % (icever, icever)):
    print>>sys.stderr, "ERROR: tar command failed"
    sys.exit(1)

if os.system("gzip -9 " + icever + ".tar"):
    print>>sys.stderr, "ERROR: gzip command failed"
    sys.exit(1)

if verbose:
    quiet = ""
else:
    quiet = "q"
    
if os.system("zip -9r" + quiet + " " + icever + ".zip " + icever):
    print>>sys.stderr, "ERROR: zip command failed"
    sys.exit(1)

#
# Copy CHANGES
#
shutil.copyfile(os.path.join(icever, "CHANGES"), "Ice-" + version + "-CHANGES")

#
# Done.
#
print "Cleaning up..."
shutil.rmtree(icever)
print "Done."
