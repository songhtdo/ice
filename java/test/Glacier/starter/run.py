#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003
# ZeroC, Inc.
# Billerica, MA, USA
#
# All Rights Reserved.
#
# Ice is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# **********************************************************************

import os, sys

for toplevel in [".", "..", "../..", "../../..", "../../../.."]:
    toplevel = os.path.normpath(toplevel)
    if os.path.exists(os.path.join(toplevel, "config", "TestUtil.py")):
        break
else:
    raise "can't find toplevel directory!"

sys.path.append(os.path.join(toplevel, "config"))
import TestUtil

if not os.environ.has_key('ICE_HOME'):
    print "ICE_HOME is not defined."
    sys.exit(0)

ice_home = os.environ['ICE_HOME']

starter = os.path.join(ice_home, "bin", "glacierstarter")
router = os.path.join(ice_home, "bin", "glacierrouter")

command = starter + TestUtil.clientServerOptions + \
          r' --Ice.PrintProcessId' \
          r' --Glacier.Starter.RouterPath=' + router + \
          r' --Glacier.Starter.PropertiesOverride=Ice.ServerIdleTime=10' \
          r' --Glacier.Starter.CryptPasswords="' + toplevel + r'/test/Glacier/starter/passwords"' + \
          r' --Glacier.Starter.Endpoints="default -p 12346 -t 5000"' + \
          r' --Glacier.Router.Endpoints="default"' + \
          r' --Glacier.Router.Client.Endpoints="default"' + \
          r' --Glacier.Router.Server.Endpoints="tcp"'

print "starting glacier starter...",
starterPipe = os.popen(command)
TestUtil.getServerPid(starterPipe)
TestUtil.getAdapterReady(starterPipe)
print "ok"

name = os.path.join("Glacier", "starter")
testdir = os.path.join(toplevel, "test", name)
os.environ["CLASSPATH"] = os.path.join(testdir, "classes") + TestUtil.sep + os.getenv("CLASSPATH", "")

TestUtil.mixedClientServerTest()

# We run the test again, to check whether the glacier router starter
# can start up multiple routers.
TestUtil.mixedClientServerTest()

print "shutting down glacier starter...",
TestUtil.killServers() # TODO: Graceful shutdown.
print "ok"

starterStatus = starterPipe.close()

if starterStatus:
    TestUtil.killServers()
    #sys.exit(1) # TODO: Uncomment when when we have graceful shutdown.

sys.exit(0)
