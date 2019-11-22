package com.example.config;

import org.springframework.cloud.aws.messaging.core.QueueMessageUtils;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import com.amazonaws.services.sqs.AmazonSQSAsync;

import org.springframework.cloud.aws.messaging.core.QueueMessagingTemplate;

import com.example.core.MyListener;
import com.example.sqs.MySqsListener;


@Configuration
@Profile("sqs")
@ComponentScan("com.example.sqs")

public class SqsConfig {

	@Bean
	MyListener myListener () {
		return new MySqsListener ();
	}
	
	@Bean
	public QueueMessagingTemplate queueMessagingTemplate(
	  AmazonSQSAsync amazonSQSAsync) {
	    return new QueueMessagingTemplate(amazonSQSAsync);
	}
}
