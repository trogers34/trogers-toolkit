package com.example.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

import com.example.core.MyListener;
import com.example.custom.MyCustomListener;

@Configuration
@Profile("custom")

@ComponentScan("com.example.custom")
public class CustomConfig {
	
	 Logger logger = LoggerFactory.getLogger(CustomConfig.class);

	public CustomConfig () {
		logger.debug("CUSTOM CONFIG");
	}

	@Bean
	MyListener myListener () {
		logger.info("CUSTOM CONFIG");
		return new MyCustomListener ();
	}
	



}
