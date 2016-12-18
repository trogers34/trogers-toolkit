package com.example;

import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;


public class MyExampleMock implements MyExample {

	@Override
	public void helloWorld() {
		System.err.println("Mock XXXXXXXXXXXX");

	}

}
