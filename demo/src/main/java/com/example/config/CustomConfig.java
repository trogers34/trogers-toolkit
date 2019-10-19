package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

import com.example.MyListener;
import com.example.custom.MyCustomListener;

@Configuration
@Profile("custom")

@ComponentScan("com.example.custom")
public class CustomConfig {

	public CustomConfig () {
		System.out.println("CUSTOM CONFIG");
	}

	@Bean
	MyListener myListener () {
		return new MyCustomListener ();
	}
	



}
