package JMeter.BookExample;

import java.io.IOException;

import org.junit.Test;

/**
 * Unit test for simple App.
 */
public class AppTest {

	@Test
	public void justTestMe() {
		App myApp = new App();
		try {
			String jsonObject = myApp.doParse();
			int bookSize = myApp.checkBookSize(jsonObject);
			System.out.println("Book Size: " + bookSize);
			bookSize = myApp.checkBookSizeNoFilter(jsonObject);
			System.out.println("Book Size No Filter: " + bookSize);
			String color = myApp.getBikeColor(jsonObject);
			System.out.println("Color: " + color);
			String title = myApp.getFirstBookTitle(jsonObject);
			System.out.println("Title: " + title);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
