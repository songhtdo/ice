// **********************************************************************
//
// Copyright (c) 2003
// ZeroC, Inc.
// Billerica, MA, USA
//
// All Rights Reserved.
//
// Ice is free software; you can redistribute it and/or modify it under
// the terms of the GNU General Public License version 2 as published by
// the Free Software Foundation.
//
// **********************************************************************

public class TestI extends _TestDisp
{
    TestI(Ice.ObjectAdapter adapter)
    {
	_adapter = adapter;

	Ice.Object servant = new HelloI();
	_adapter.add(servant, Ice.Util.stringToIdentity("hello"));
    }

    public void
    shutdown(Ice.Current current)
    {
	_adapter.getCommunicator().shutdown();
    }

    public HelloPrx
    getHello(Ice.Current current)
    {
	return HelloPrxHelper.uncheckedCast(_adapter.createProxy(Ice.Util.stringToIdentity("hello")));
    }

    private Ice.ObjectAdapter _adapter;
}
