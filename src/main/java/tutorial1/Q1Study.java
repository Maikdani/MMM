package tutorial1;

import java.util.Calendar;

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
		PersistenceMechanism writer = new CSVFile("C:/Users/Maikel/Documents/GitHub/SA/csv/bugzillaCat1.csv");
		initWriter(writer);
		
		Calendar date = Calendar.getInstance();
		date.set(2016, 0, 1);
		new RepositoryMining()
			.in(GitRepository.singleProject("C:/Users/Maikel/Documents/GitHub/SA/projects/bugzilla"))
			.through(Commits.since(date))
			.process(new DevelopersVisitor(), writer)
			.mine();
		
		PersistenceMechanism writer2 = new CSVFile("C:/Users/Maikel/Documents/GitHub/SA/csv/bugzillaCat2.csv");
		initWriter2(writer2);
		
		new RepositoryMining()
		.in(GitRepository.singleProject("C:/Users/Maikel/Documents/GitHub/SA/projects/bugzilla"))
		.through(Commits.since(date))
		.process(new Category2(), writer2)
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
				"LT"
		);
	}

}
