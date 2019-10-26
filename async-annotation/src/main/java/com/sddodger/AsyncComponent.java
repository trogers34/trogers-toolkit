package com.sddodger;

import java.util.concurrent.Future;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.AsyncResult;
import org.springframework.stereotype.Component;

@Component
public class AsyncComponent {
	
	@Autowired
	private DoAsync doAsync;

    @Async
    public void asyncMethodWithVoidReturnType() {
    	try {
			Thread.sleep(100);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        System.out.println("BEGIN - Execute method asynchronously. " + Thread.currentThread().getName());
        doAsync.asyncMethodWithVoidReturnType(Thread.currentThread().getName());
        System.out.println("END - Execute method asynchronously. " + Thread.currentThread().getName());
    }

    @Async
    public Future<String> asyncMethodWithReturnType() {
        System.out.println("Execute method asynchronously " + Thread.currentThread().getName());
        try {
            Thread.sleep(5000);
            return new AsyncResult<>("hello world !!!!");
        } catch (final InterruptedException e) {

        }

        return null;
    }

    @Async("threadPoolTaskExecutor")
    public void asyncMethodWithConfiguredExecutor() {
        System.out.println("Execute method asynchronously with configured executor" + Thread.currentThread().getName());
    }

    @Async
    public void asyncMethodWithExceptions() throws Exception {
        throw new Exception("Throw message from asynchronous method. ");
    }

}