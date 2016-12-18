package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MyExampleConfig {
	@Bean
	public MyExample myExample () {
		return new MyExampleImpl();
	}
}
