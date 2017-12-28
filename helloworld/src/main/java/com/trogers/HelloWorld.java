package com.trogers;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HelloWorld {
    private static final Logger logger =
            LoggerFactory.getLogger(HelloWorld.class);

    public void doSomeLogging (String logMe) {
        logger.debug("XXXXXXXXXXXX: " + logMe);
    }
}
