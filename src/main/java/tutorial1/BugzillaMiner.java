package tutorial1;

import org.repodriller.domain.Commit;
import org.repodriller.persistence.PersistenceMechanism;
import org.repodriller.scm.CommitVisitor;
import org.repodriller.scm.SCMRepository;

public class BugzillaMiner implements CommitVisitor {
	
	public void process(SCMRepository repo, Commit commit, PersistenceMechanism writer) {
		String bugID = findBugID(commit.getMsg());
		if(bugID != null)
			writer.write(
					commit.getHash(),
					bugID
			);
	}

	
	public String findBugID(String msg) {
		msg = msg.toLowerCase();
		
		if(msg.contains("bug")) {
			int index = msg.indexOf("bug");
			if(index + 4 < msg.length())
				msg = msg.substring(index + 4);
			int i = 0;
			while (i < msg.length() && Character.isDigit(msg.charAt(i))) i++;
			if(i == 0)
				return null;
			msg = msg.substring(0, i);
			return msg;
		} else {
			return null;
		}
	}
}
