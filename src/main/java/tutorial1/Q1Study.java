package tutorial1;

import java.util.Calendar;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.log4j.BasicConfigurator;
import org.repodriller.RepoDriller;
import org.repodriller.RepositoryMining;
import org.repodriller.Study;
import org.repodriller.filter.range.Commits;
import org.repodriller.persistence.PersistenceMechanism;
import org.repodriller.persistence.csv.CSVFile;
import org.repodriller.scm.GitRepository;

public class Q1Study implements Study {

	public static void main(String[] args) {		
		BasicConfigurator.configure();
		new RepoDriller().start(new Q1Study());
	}
	
	
	public void execute() {		
		Calendar date = Calendar.getInstance();
		date.set(2016, 0, 1);
		
		//startCat1(date);
		startCat2(date);
	}
	
	public void startCat1(Calendar date) {
		PersistenceMechanism writer = new CSVFile("csv/bugzillaCat1.csv");
		initWriter(writer);
		
		new RepositoryMining()
		.in(GitRepository.singleProject("projects/bugzilla"))
		.through(Commits.since(date))
		.withThreads(4)
		.process(new DevelopersVisitor(), writer)
		.mine();
	}
	
	public void startCat2(Calendar date) {
		PersistenceMechanism writer2 = new CSVFile("csv/bugzillaCat2.csv");
		initWriter2(writer2);
		
		new RepositoryMining()
		.in(GitRepository.singleProject("projects/bugzilla"))
		.through(Commits.since(date))
		.withThreads(4)
		.process(new Category2(), writer2)
		.mine();
	}
	
	public void startBugMiner(Calendar date) {
		PersistenceMechanism writer3 = new CSVFile("csv/bugzillaBugIDS.csv");
		initWriter3(writer3);
		
		new RepositoryMining()
		.in(GitRepository.singleProject("projects/bugzilla"))
		.through(Commits.since(date))
		.withThreads(4)
		.process(new BugzillaMiner(), writer3)
		.mine();
	}
	
	public void initWriter(PersistenceMechanism writer) {
		writer.write(
				"Hash",
				"Paths",
				"NS",
				"ND",
				"NF",
				"Entropy"
		);
	}
	
	public void initWriter2(PersistenceMechanism writer) {
		writer.write(
				"Hash",
				"File",
				"LA",
				"LD",
				"LT",
				"isAdded",
				"isRemoved"
		);
	}
	
	public void initWriter3(PersistenceMechanism writer) {
		writer.write(
				"Hash",
				"ID"
		);
	}

}
