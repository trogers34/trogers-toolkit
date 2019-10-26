package com.sddodger;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class DoAsync {
	
	@Async
	public void asyncMethodWithVoidReturnType(String parentName) {
		try {
			Thread.sleep(100);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	    System.out.println("Execute method asynchronously. "
	      + Thread.currentThread().getName() + " PARENT " + parentName
	      );
	}

}
