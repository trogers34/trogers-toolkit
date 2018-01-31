package com.example;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@RestController
@EnableAutoConfiguration
public class Example {

	@Autowired
	MyExample myExample;

	@RequestMapping("/")
	String home() {
		myExample.helloWorld();
		return "Hello World!";

	}

	@RequestMapping(method = RequestMethod.POST, value = "/employee")
	public String addEmployee(@RequestBody String body) {
		System.out.println("Elvis has left the building");
		return "<user></user>";
	}
}
