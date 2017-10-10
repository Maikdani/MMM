package main;

import org.repodriller.RepoDriller;
import org.repodriller.Study;

public class FirstStudy implements Study {

	public static void main(String[] args) {
		new RepoDriller().start(new FirstStudy());
	}

	public void execute() {
		
	}
}
