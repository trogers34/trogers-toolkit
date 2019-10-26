package com.sddodger.config;


import java.util.concurrent.Executor;

import org.springframework.aop.interceptor.AsyncUncaughtExceptionHandler;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.SimpleAsyncTaskExecutor;
import org.springframework.scheduling.annotation.AsyncConfigurer;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import com.sddodger.CustomAsyncExceptionHandler;

@Configuration
@EnableAsync
@ComponentScan("com.sddodger")
public class SpringAsyncConfig implements AsyncConfigurer{
     
	 @Bean(name = "threadPoolTaskExecutor")
	    public Executor threadPoolTaskExecutor() {
	        return new ThreadPoolTaskExecutor();
	    }

	    public Executor getAsyncExecutor() {
	        return new SimpleAsyncTaskExecutor();
	    }

	    public AsyncUncaughtExceptionHandler getAsyncUncaughtExceptionHandler() {
	        return new CustomAsyncExceptionHandler();
	    }
}