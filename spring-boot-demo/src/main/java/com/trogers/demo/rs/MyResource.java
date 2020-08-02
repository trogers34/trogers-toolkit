package com.trogers.demo.rs;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MyResource {
	
	@RequestMapping ("/hello")
	public String helloWorld () {
		return "testString";
	}
}
