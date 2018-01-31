package com.trogers;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;

@RestController
public class HelloController {
    private static final Logger logger =
            LoggerFactory.getLogger(HelloController.class);

    @RequestMapping("/")
    public String index() {
        logger.info("AAAAAAAAAAAAAA");
        logger.info("YYYYYYYYYYYYYY");
        return "Greetings from Spring Boot!";
    }
    @RequestMapping("/2")
    public String index2() {
        logger.info("BBBBBBBBBBBBBB");
        logger.info("TTTTTTTTTTTTTT");
        return "Greetings from Spring Boot!";
    }
}
