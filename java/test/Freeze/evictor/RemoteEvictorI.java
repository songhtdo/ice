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

public final class RemoteEvictorI extends Test._RemoteEvictorDisp
{
    RemoteEvictorI(Ice.ObjectAdapter adapter, String category, Freeze.DB db, Freeze.Evictor evictor)
    {
        _adapter = adapter;
        _category = category;
        _db = db;
        _evictor = evictor;
        _lastSavedValue = -1;
    }

    public void
    setSize(int size, Ice.Current current)
    {
        _evictor.setSize(size);
    }

    public Test.ServantPrx
    createServant(int value, Ice.Current current)
    {
        Ice.Identity id = new Ice.Identity();
        id.category = _category;
        id.name = "" + value;
        ServantI servant = new ServantI(this, _evictor, value);
        _evictor.createObject(id, servant);
        return Test.ServantPrxHelper.uncheckedCast(_adapter.createProxy(id));
    }

    public int
    getLastSavedValue(Ice.Current current)
    {
        int result = _lastSavedValue;
        _lastSavedValue = -1;
        return result;
    }

    public void
    clearLastSavedValue(Ice.Current current)
    {
        _lastSavedValue = -1;
    }

    public void
    deactivate(Ice.Current current)
    {
        _adapter.removeServantLocator(_category);
        _adapter.remove(Ice.Util.stringToIdentity(_category));
        _db.close();
    }

    void
    setLastSavedValue(int value)
    {
        _lastSavedValue = value;
    }

    private Ice.ObjectAdapter _adapter;
    private String _category;
    private Freeze.DB _db;
    private Freeze.Evictor _evictor;
    private int _lastSavedValue;
}
