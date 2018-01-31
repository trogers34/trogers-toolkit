package JMeter.BookExample;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.IOUtils;

import com.jayway.jsonpath.Criteria;
import com.jayway.jsonpath.Filter;
import com.jayway.jsonpath.JsonPath;

/**
 * Hello world!
 *
 */
public class App {
	public String doParse() throws IOException {

		String fileName = "Books.json";
		ClassLoader classLoader = this.getClass().getClassLoader();
		File file = new File(classLoader.getResource(fileName).getFile());

		// File is found
		System.out.println("File Found : " + file.exists());

		// Read File Content
		String content = new String(Files.readAllBytes(file.toPath()));
		System.out.println(content);
		return content;
	}

	public int checkBookSize(String data) {

		// Object json = new String(data);
		List categories = new ArrayList();
		categories.add("fiction");
		categories.add("reference");
		Filter filter = Filter.filter(Criteria.where("category").in(categories));
		List books = JsonPath.read(data, "$.store.book[?]", new Filter[] { filter });
		// List books = JsonPath.parse(data).read("$.store.book[?]", new
		// Filter[] {filter});

		return books.size();
	}
	
	public int checkBookSizeNoFilter(String data) {

		// Object json = new String(data);

		
		List books = JsonPath.read(data, "$.store.book");
		

		return books.size();
	}
	
	public String getFirstBookTitle(String data) {

		String title = JsonPath.read(data, "$.store.book[0].title");
		// List books = JsonPath.parse(data).read("$.store.book[?]", new
		// Filter[] {filter});

		return title;
	}
	
	public String getBikeColor (String data) {
		
		String color = JsonPath.read(data, "$.store.bicycle.color");
		return color;
	}

	public static void main(String[] args) {
		System.out.println("Hello World!");

		App myApp = new App();
		ClassLoader classLoader = myApp.getClass().getClassLoader();
		// File file = new
		// File(classLoader.getResource("Books.json").getFile());

		String result = "";

		try {
			result = IOUtils.toString(classLoader.getResourceAsStream("Books.json"));
		} catch (IOException e) {
			e.printStackTrace();
		}
		System.out.println("JSON:" + result);
	}
}
