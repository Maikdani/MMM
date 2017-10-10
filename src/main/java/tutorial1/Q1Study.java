package tutorial1;

import java.util.Calendar;

import org.repodriller.RepoDriller;
import org.repodriller.RepositoryMining;
import org.repodriller.Study;
import org.repodriller.filter.range.Commits;
import org.repodriller.persistence.PersistenceMechanism;
import org.repodriller.persistence.csv.CSVFile;
import org.repodriller.scm.GitRepository;

public class Q1Study implements Study {

	public static void main(String[] args) {
		new RepoDriller().start(new Q1Study());
	}
	
	
	public void execute() {
		PersistenceMechanism writer = new CSVFile("C:/Users/Maikel/Documents/GitHub/SA/csv/bugzilla.csv");
		initWriter(writer);
		
		Calendar date = Calendar.getInstance();
		date.set(2016, 0, 1);
		new RepositoryMining()
			.in(GitRepository.singleProject("C:/Users/Maikel/Documents/GitHub/SA/projects/bugzilla"))
			.through(Commits.since(date))
			.process(new DevelopersVisitor(), writer)
			.mine();
	}
	
	public void initWriter(PersistenceMechanism writer) {
		writer.write(
				"Hash",
				"Paths",
				"NS",
				"ND",
				"NF",
				"Entropy",
				"LA",
				"LD",
				"LT",
				"FIX",
				"Refactor"
		);
	}

}
