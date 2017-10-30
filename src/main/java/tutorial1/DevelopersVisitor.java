package tutorial1;

import java.util.ArrayList;

import org.repodriller.domain.Commit;
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
					getFIX(commit)
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
	public double getEntropy(Commit commit) {
		int temp = 0;
		int sum = 0;
		int[] numMods = new int[commit.getModifications().size()];
		int i = 0;
		
		for(Modification m : commit.getModifications()) {
			temp = m.getAdded();
			temp += m.getRemoved();
			numMods[i] = temp;
			i++;
			sum += temp;
		}
		
		double entropy = 0;
		double fraction = 0;
		
		for(int numMod : numMods) {
			if(numMod != 0){
				fraction = (double)numMod/sum;
				entropy -= fraction*(Math.log10(fraction)/Math.log10(2));
			}
		}
		
		return entropy;
	}
	public String getModifications(Commit commit) {
		String modifications = "["; 
		for(Modification m : commit.getModifications()) {
			modifications += m.getFileName() + ", ";
		}
		int end = modifications.length()-2;
		if(end < 0)
			end = 0;
		modifications = modifications.substring(0, end);
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
	
	public boolean getFIX(Commit commit) {
		String msg = commit.getMsg().toLowerCase();
		if(msg.contains("bug"))
			return true;
		else if(msg.contains("fix"))
			return true;
		else if(msg.contains("defect"))
			return true;
		else if(msg.contains("patch"))
			return true;
		else
			return false;
	}

}