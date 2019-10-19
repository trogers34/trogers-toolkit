package com.trogers34.userportal;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping({ "/user-portal/users" })
public class UserController {
	Logger log = LogManager.getRootLogger();

	// @Autowired
	// private UserService userService;

	private User buildUserObject(int id) {
		User user = new User();
		user.setId(id);
		user.setEmail("tim@trogers.com");
		user.setFirstName("Tim");
		user.setLastName("Royers");
		return user;
	}

	@PostMapping
	public User create(@RequestBody User user) {
		log.info("first name: ", user.getFirstName());
		log.info("last name: ", user.getLastName());
		log.info("email: ", user.getEmail());
		return user;
	}

	@GetMapping(path = { "/{id}" })
	public User findOne(@PathVariable("id") int id) {
		return buildUserObject(id);
	}

	@PutMapping
	public User update(@RequestBody User user) {
		log.info("first name: ", user.getFirstName());
		log.info("last name: ", user.getLastName());
		log.info("email: ", user.getEmail());
		return user;
	}

	@DeleteMapping(path = { "/{id}" })
	public User delete(@PathVariable("id") int id) {
		return buildUserObject(id);
	}

}
