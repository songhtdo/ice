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

#ifndef CLOCK_I_H
#define CLOCK_I_H

#include <Clock.h>

class ClockI : public Clock
{
public:

    virtual void tick(const Ice::Current&);
};

#endif
