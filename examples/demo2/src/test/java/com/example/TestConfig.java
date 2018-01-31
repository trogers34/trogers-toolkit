package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

@Configuration
//@ComponentScan(basePackages = {"com.example"})
@Profile("test")
public class TestConfig {

	@Bean
	public MyExample myExample () {
		return new MyExampleMock();
	}
}
