package com.example.sqs;
import org.springframework.stereotype.Component;

import com.example.core.MyListener;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.aws.messaging.core.QueueMessagingTemplate;
import org.springframework.cloud.aws.messaging.listener.annotation.SqsListener;

@Component
public class MySqsListener  implements MyListener {
	
	public MySqsListener () {
		System.out.println("SQS SQS");
	}
	
	@Autowired
	QueueMessagingTemplate messagingTemplate;
	  
	public void send(String topicName, Object message) {
	    messagingTemplate.convertAndSend(topicName, message);
	}
	
	@SqsListener("queueName")
	public void queueListener(String person) {
		// ...
	}
}
