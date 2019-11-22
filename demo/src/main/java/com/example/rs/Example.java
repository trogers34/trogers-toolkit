package com.example.rs;

import java.io.InputStream;

import org.apache.commons.io.IOUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.core.MyListener;

@RestController
@EnableAutoConfiguration
public class Example {
	
	public Example () {
		System.err.println("EXAMPLE");
	}
	
	@Autowired
	MyListener myListener;
	

    @RequestMapping("/home")
    String home() {
    	try {
    		ClassPathResource classPathResource = new ClassPathResource("json/temp.json");
    		InputStream inputStream = classPathResource.getInputStream();
    		String content = IOUtils.toString(inputStream, "UTF-8") ;
    		System.out.println("" + content);
    		} catch (Exception e) {
    			e.printStackTrace();
    		}
        return "Hello World!";
    }
}
	