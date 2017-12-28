package com.trogers;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MetricThingy {
    private static final Logger logger =
            LoggerFactory.getLogger(MetricThingy.class);

    public void logMeAgain (String log) {
        logger.debug("ZZZZZZZZZZZ: " + log);
    }
}
