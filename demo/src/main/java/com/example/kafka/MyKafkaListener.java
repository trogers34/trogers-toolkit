package com.example.kafka;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import com.example.MyListener;


@Component

public class MyKafkaListener implements MyListener{
	
	public MyKafkaListener () {
		System.out.println("KAFKA KAFKA");
	}
	@KafkaListener(topics = "topicName", groupId = "foo")
	public void listen(String message) {
	    System.out.println("Received Messasge in group foo: " + message);
	}	

}
