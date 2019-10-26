package com.sddodger;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.support.AnnotationConfigContextLoader;

import com.sddodger.config.SpringAsyncConfig;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes = { SpringAsyncConfig.class }, loader = AnnotationConfigContextLoader.class)
public class AsyncAnnotationExampleIntegrationTest {

	@Autowired
	private AsyncComponent asyncAnnotationExample;

	// tests

	@Test
	public void testAsyncAnnotationForMethodsWithVoidReturnType() {
		for (int i = 0; i < 1000; i++) {
			System.out.println("Start - invoking an asynchronous method. " + Thread.currentThread().getName());
			asyncAnnotationExample.asyncMethodWithVoidReturnType();
			System.out.println("End - invoking an asynchronous method. ");
		}
	}

	public void testAsyncAnnotationForMethodsWithReturnType() throws InterruptedException, ExecutionException {
		System.out.println("Start - invoking an asynchronous method. " + Thread.currentThread().getName());
		final Future<String> future = asyncAnnotationExample.asyncMethodWithReturnType();

		while (true) {
			if (future.isDone()) {
				System.out.println("Result from asynchronous process - " + future.get());
				break;
			}
			System.out.println("Continue doing something else. ");
			Thread.sleep(1000);
		}
	}

	public void testAsyncAnnotationForMethodsWithConfiguredExecutor() {
		System.out.println("Start - invoking an asynchronous method. ");
		asyncAnnotationExample.asyncMethodWithConfiguredExecutor();
		System.out.println("End - invoking an asynchronous method. ");
	}

	public void testAsyncAnnotationForMethodsWithException() throws Exception {
		System.out.println("Start - invoking an asynchronous method. ");
		asyncAnnotationExample.asyncMethodWithExceptions();
		System.out.println("End - invoking an asynchronous method. ");
	}

}
