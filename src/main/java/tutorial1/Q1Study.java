package tutorial1;

import java.util.ArrayList;
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
	private ArrayList<Calendar> fromDates;
	private ArrayList<Calendar> toDates;
	
	private String[] startDates = {"2005-01-01", "1999-01-01", "2012-01-01", "2009-11-01", "2008-07-01", "2008-07-01", "2008-07-01", "2010-08-01", "2013-06-01", "2006-11-01", "2007-01-01"};
	private String[] endDates = {"2009-01-01", "2013-03-01", "2014-01-01", "2011-05-31", "2011-04-01", "2016-02-01",  "2012-10-01", "2012-01-01", "2014-08-01", "2008-10-01", "2012-10-01"};
	
	private String[] projectNames = {"bugzilla", "rhino", "bedrock", "otrs", "tomcat", "jmeter", "activemq", "camel", "hadoop", "wicket", "maven"};
	
	private String projects = "SZZ/projects/";
	private String csvs = "SZZ/csv/";

	public static void main(String[] args) {		
		BasicConfigurator.configure();
		new RepoDriller().start(new Q1Study());
	}
	
	
	public void execute() {		
		// Test with only 10 days
		/* 
		String[] testStartDates = {"2002-01-01", "1999-01-01", "2012-01-01", "2008-11-01", "2007-01-01", "2004-04-01", "2008-07-01", "2009-12-01", "2012-06-01", "2006-11-01", "2007-01-01"};
		String[] testEndDates = {"2002-01-11", "1999-01-11", "2012-01-11", "2008-11-11", "2007-01-11", "2004-04-11", "2008-07-11", "2009-12-11", "2012-06-11", "2006-11-11", "2007-01-11"};	
		startDates = testStartDates;
		endDates = testEndDates;
		*/
		fromDates = getDates(startDates);
		toDates = getDates(endDates);
		int index = 0;
		boolean singleProject = false;
		
		
		while(index < projectNames.length) {
			startCat1(projectNames[index], fromDates.get(index), toDates.get(index));
			// startCat2(projectNames[index], fromDates.get(index), toDates.get(index));
			if(singleProject)
				break;
			index++;
		}
	}
	
	public ArrayList<Calendar> getDates(String[] dates) {
		String[] curDate;
		ArrayList<Calendar> datesList = new ArrayList<Calendar>();
		for(String date : dates) {
			curDate = date.split("-");
			Calendar newdate = Calendar.getInstance();
			newdate.set(Integer.parseInt(curDate[0]), Integer.parseInt(curDate[1]), Integer.parseInt(curDate[2]));
			datesList.add(newdate);
		}
		return datesList;
	}
	
	public void startCat1(String project, Calendar from, Calendar to) {
		PersistenceMechanism writer = new CSVFile(csvs + project + "Cat1.csv");
		initWriter(writer);
		
		new RepositoryMining()
		.in(GitRepository.singleProject(projects + project))
		.through(Commits.betweenDates(from, to))
		.withThreads(4)
		.process(new DevelopersVisitor(), writer)
		.mine();
	}
	
	public void startCat2(String project, Calendar from, Calendar to) {
		PersistenceMechanism writer2 = new CSVFile(csvs + project + "Cat2.csv");
		initWriter2(writer2);
		
		new RepositoryMining()
		.in(GitRepository.singleProject(projects + project))
		.through(Commits.betweenDates(from, to))
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
				"Entropy",
				"FIX"
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
