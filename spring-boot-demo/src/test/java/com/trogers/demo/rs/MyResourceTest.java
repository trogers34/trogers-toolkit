package com.trogers.demo.rs;


import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;

import com.trogers.demo.boot.SpringBootDemoApplication;

//@ExtendWith(SpringExtension.class)
//@RunWith(SpringJUnit4ClassRunner.class)
//@RunWith(SpringRunner.class)
//@ContextConfiguration
@SpringBootTest(classes = SpringBootDemoApplication.class, webEnvironment = WebEnvironment.DEFINED_PORT)

//@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
//@ContextConfiguration(classes = { ApplicationConfig.class })

public class MyResourceTest {
	
	
	@LocalServerPort
	private int port;

	@Autowired
	TestRestTemplate restTemplate;

	HttpHeaders headers = new HttpHeaders();

	@Test
	public void test() {
		HttpEntity<String> entity = new HttpEntity<String>(null, headers);

		ResponseEntity<String> response = restTemplate.exchange(createURLWithPort("/hello"), HttpMethod.GET,
				entity, String.class);

		String expected = "testString";
		assertThat(response.getBody()).isEqualTo(expected);
	}

	private String createURLWithPort(String uri) {
		String retVal = "http://localhost:" + port + uri;
		
		System.out.println("XXXXXX: " + retVal);
		
		return retVal;
	}
}
