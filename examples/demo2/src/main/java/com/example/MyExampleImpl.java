package com.example;

import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Service;


public class MyExampleImpl implements MyExample {

	@Override
	public void helloWorld() {
		System.err.println("Real output");
		
	}

}
