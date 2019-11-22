package com.example.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.stereotype.Component;

import com.example.core.MyListener;
import com.example.kafka.MyKafkaListener;
import com.example.sqs.MySqsListener;

@Configuration
@Profile("kafka")
@EnableKafka
@ComponentScan("com.example.kafka")
public class KafkaConfig {

	public KafkaConfig () {
		System.out.println("KAFKA CONFIG");
	}

	@Bean
	MyListener myListener () {
		return new MyKafkaListener ();
	}
	
}
