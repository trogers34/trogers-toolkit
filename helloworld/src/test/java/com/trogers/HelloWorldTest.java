package com.trogers;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;


@RunWith(SpringJUnit4ClassRunner.class)
public class HelloWorldTest {

    @Test
    public void oneLog () {
        HelloWorld hw = new HelloWorld();
        hw.doSomeLogging("XXXXX");
    }

    @Test
    public void twoLog () {
        MetricThingy mt = new MetricThingy();
        mt.logMeAgain("ZZZZZZZ");
    }

}