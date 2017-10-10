package tutorial1;

import java.util.ArrayList;
import java.util.List;

import org.repodriller.domain.Commit;
import org.repodriller.domain.DiffBlock;
import org.repodriller.domain.DiffLine;
import org.repodriller.domain.DiffParser;
import org.repodriller.domain.Modification;
import org.repodriller.persistence.PersistenceMechanism;
import org.repodriller.scm.CommitVisitor;
import org.repodriller.scm.SCMRepository;

public class DevelopersVisitor implements CommitVisitor {

	public void process(SCMRepository repo, Commit commit, PersistenceMechanism writer) {
			writer.write(
					commit.getHash(),
					getModifications(commit),
					getNS(commit),
					getND(commit),
					getNF(commit),
					getEntropy(commit),
					getLA(commit),
					getLD(commit),
					getLT(commit)
			);
	}

	public String name() {
		return "developers";
	}
	
	/**
	 * Get Number of modified subsystems
	 * @param commit
	 * @return
	 */
	public String getNS(Commit commit) {
		ArrayList<String> subs = new ArrayList<String>();
		String subsystem;
		for(Modification m : commit.getModifications()) {
			subsystem = getSubsystem(m.getFileName());
			if(!subs.contains(subsystem))
				subs.add(subsystem);
		}
		
		return Integer.toString(subs.size());
	}
	/**
	 * Get Number of modified directories
	 * @param commit
	 * @return
	 */
	public String getND(Commit commit) {
		ArrayList<String> dirs = new ArrayList<String>();
		String dir;
		for(Modification m : commit.getModifications()) {
			dir = getDir(m.getFileName());
			if(!dirs.contains(dir))
				dirs.add(dir);
		}
		
		return Integer.toString(dirs.size());
	}
	/**
	 * Get Number of modified files
	 * @param commit
	 * @return
	 */
	public String getNF(Commit commit) {
		ArrayList<String> files = new ArrayList<String>();
		for(Modification m : commit.getModifications()) {
			if(!files.contains(m.getFileName()))
				files.add(m.getFileName());
		}
		
		return Integer.toString(files.size());
	}
	/**
	 * Get Distribution of modified code across each file
	 * @param commit
	 * @return
	 */
	public String getEntropy(Commit commit) {
		return "";
	}
	/**
	 * Get Lines of code added
	 * @param commit
	 * @return
	 */
	public String getLA(Commit commit) {
		DiffParser parsedDiff;
		int count = 0;
		for(Modification m : commit.getModifications()) {
			parsedDiff = new DiffParser(m.getDiff());
			count += countAdded(parsedDiff.getBlocks());
		}
		return Integer.toString(count);
	}
	
	public int countAdded(List<DiffBlock> diffBlock) {
		List<DiffLine> diffLines;
		int count = 0;
		
		for(int i = 0; i < diffBlock.size(); i++) {
			diffLines = diffBlock.get(i).getLinesInNewFile();
			for(DiffLine line : diffLines)
				if(line.getType().name().equals("ADDED"))
					count++;
		}
		
		return count;
	}
	
	/**
	 * Lines of code deleted
	 * @param commit
	 * @return
	 */
	public String getLD(Commit commit) {
		DiffParser parsedDiff;
		int count = 0;
		for(Modification m : commit.getModifications()) {
			parsedDiff = new DiffParser(m.getDiff());
			count += countRemoved(parsedDiff.getBlocks());
		}
		return Integer.toString(count);
	}
	
	public int countRemoved(List<DiffBlock> diffBlock) {
		List<DiffLine> diffLines;
		int count = 0;
		
		for(int i = 0; i < diffBlock.size(); i++) {
			diffLines = diffBlock.get(i).getLinesInOldFile();
			for(DiffLine line : diffLines)
				if(line.getType().name().equals("REMOVED"))
					count++;
		}
		
		return count;
	}
	/**
	 * Get Lines of code in a file before the change
	 * @param commit
	 * @return
	 */
	public String getLT(Commit commit) {
		return "";
	}
	
	public String getModifications(Commit commit) {
		String modifications = "["; 
		for(Modification m : commit.getModifications()) {
			modifications += m.getFileName() + ", ";
		}
		modifications = modifications.substring(0, modifications.length()-2);
		return modifications + "]";
	}
	
	public String getDir(String filePath) {
		String dir;
		if(filePath.contains("/"))
			dir = filePath.substring(0, filePath.lastIndexOf("/"));
		else
			return "";
		return dir;
	}
	
	public String getSubsystem(String filePath) {
		String subsystem;
		if(filePath.contains("/"))
			subsystem = filePath.substring(0, filePath.indexOf("/"));
		else
			return "";
		return subsystem;
	}

}