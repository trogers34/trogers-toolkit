package hello;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController 
@RequestMapping(value = "/hello")
public class DockerRestApplication {
	
    private static final Logger log = LoggerFactory.getLogger(DockerRestApplication.class);
    
    @RequestMapping(value = "/bar", method = RequestMethod.GET)
    public String bar() {
    	log.info("bar");
        return "Bye Docker World";
    }
    
    @RequestMapping(value = "/foo", method = RequestMethod.GET)
    public String foo() {
    	log.info("foo");
        return "Ugh Docker World";
    }

    
	public static void main(String[] args) {
		log.info("RUNNING XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");
		SpringApplication.run(DockerRestApplication.class, args);
	}
}
