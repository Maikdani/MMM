package tutorial1;

import java.util.List;

import org.repodriller.domain.Commit;
import org.repodriller.domain.DiffBlock;
import org.repodriller.domain.DiffLine;
import org.repodriller.domain.DiffParser;
import org.repodriller.domain.Modification;
import org.repodriller.persistence.PersistenceMechanism;
import org.repodriller.scm.CommitVisitor;
import org.repodriller.scm.SCMRepository;

public class Category2 implements CommitVisitor { 
	public void process(SCMRepository repo, Commit commit, PersistenceMechanism writer) {
		for(Modification m : commit.getModifications()) {
			writer.write(
					commit.getHash(),
					m.getFileName(),
					m.getAdded(),
					m.getRemoved(),
					//getLA(commit, m),
					//getLD(commit, m),
					getLT(commit, m),
					isAdded(m),
					isRemoved(m)
			);
		}
	}
	
	/**
	 * Get Lines of code added
	 * @param commit
	 * @return
	 */
	public String getLA(Commit commit, Modification m) {
		DiffParser parsedDiff = new DiffParser(m.getDiff());
		int count = countAdded(parsedDiff.getBlocks());
		
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
	public String getLD(Commit commit, Modification m) {
		DiffParser parsedDiff = new DiffParser(m.getDiff());
		int count = countRemoved(parsedDiff.getBlocks());
		
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
	public int getLT(Commit commit,  Modification m) {
		String sourceCode = m.getSourceCode();
		int count = 0;
		while(sourceCode.contains("\n")) {
			sourceCode = sourceCode.substring(sourceCode.indexOf("\n") + 1);
			count++;
		}
		return count;
	}
	
	public int isAdded(Modification m) {
		if(m.getType().name().equals("ADD"))
			return 1;
		return 0;
	}
	
	public int isRemoved(Modification m) {
		if(m.getType().name().equals("DELETE"))
			return 1;
		return 0;
	}
}
	

