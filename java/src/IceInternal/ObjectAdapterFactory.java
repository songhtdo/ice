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

package IceInternal;

public final class ObjectAdapterFactory
{
    public synchronized void
    shutdown()
    {
	//
	// Ignore shutdown requests if the object adapter factory has
	// already been shut down.
	//
	if(_instance == null)
	{
	    return;
	}

        java.util.Iterator i = _adapters.values().iterator();
        while(i.hasNext())
        {
            Ice.ObjectAdapter adapter = (Ice.ObjectAdapter)i.next();
            adapter.deactivate();
        }

	_instance = null;
	_communicator = null;
	
	notifyAll();
    }

    public void
    waitForShutdown()
    {
	synchronized(this)
	{
	    //
	    // First we wait for the shutdown of the factory itself.
	    //
	    while(_instance != null)
	    {
		try
		{
		    wait();
		}
		catch(InterruptedException ex)
		{
		}
	    }
	    
	    //
	    // If some other thread is currently shutting down, we wait
	    // until this thread is finished.
	    //
	    while(_waitForShutdown)
	    {
		try
		{
		    wait();
		}
		catch(InterruptedException ex)
		{
		}
	    }
	    _waitForShutdown = true;
	}
	
	//
	// Now we wait for deactivation of each object adapter.
	//
        java.util.Iterator i = _adapters.values().iterator();
        while(i.hasNext())
        {
            Ice.ObjectAdapter adapter = (Ice.ObjectAdapter)i.next();
            adapter.waitForDeactivate();
        }
	
	//
	// We're done, now we can throw away the object adapters.
	//
	_adapters.clear();

	synchronized(this)
	{
	    //
	    // Signal that waiting is complete.
	    //
	    _waitForShutdown = false;
	    notifyAll();
	}
    }
    
    public synchronized Ice.ObjectAdapter
    createObjectAdapter(String name)
    {
	if(_instance == null)
	{
	    throw new Ice.ObjectAdapterDeactivatedException();
	}

        Ice.ObjectAdapter adapter = (Ice.ObjectAdapter)_adapters.get(name);
        if(adapter != null)
        {
            return adapter;
        }

        adapter = new Ice.ObjectAdapterI(_instance, _communicator, name);
        _adapters.put(name, adapter);
        return adapter;
    }

    public synchronized Ice.ObjectAdapter
    findObjectAdapter(Ice.ObjectPrx proxy)
    {
	if(_instance == null)
	{
	    return null;
	}

        java.util.Iterator i = _adapters.values().iterator();
        while(i.hasNext())
        {
            Ice.ObjectAdapterI adapter = (Ice.ObjectAdapterI)i.next();
	    try
	    {
		if(adapter.isLocal(proxy))
		{
		    return adapter;
		}
	    }
	    catch(Ice.ObjectAdapterDeactivatedException ex)
	    {
		// Ignore.
	    }
	}

        return null;
    }

    //
    // Only for use by Instance.
    //
    ObjectAdapterFactory(Instance instance, Ice.Communicator communicator)
    {
        _instance = instance;
	_communicator = communicator;
	_waitForShutdown = false;
    }

    protected void
    finalize()
        throws Throwable
    {
	assert(_instance == null);
	assert(_communicator == null);
	assert(_adapters.size() == 0);
	assert(!_waitForShutdown);

        super.finalize();
    }

    private Instance _instance;
    private Ice.Communicator _communicator;
    private java.util.HashMap _adapters = new java.util.HashMap();
    private boolean _waitForShutdown;
}
