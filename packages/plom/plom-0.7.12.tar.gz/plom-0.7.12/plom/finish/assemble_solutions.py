# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2021 Andrew Rechnitzer

from multiprocessing import Pool
import os
from pathlib import Path
import shutil
import tempfile

from tqdm import tqdm

from plom import get_question_label
from plom.finish import start_messenger
from plom.finish.solutionAssembler import assemble
from plom.finish.coverPageBuilder import makeCover


numberOfQuestions = 0


def _parfcn(z):
    """Parallel function used below, must be defined in root of module.

    Args:
        z (tuple): Arguments to assemble and makeSolnCover.
    """
    x, y = z
    if x and y:
        makeCover(*x, solution=True)
        assemble(*y)


def checkAllSolutionsPresent(solutionList):
    # soln list = [ [q,v,md5sum], [q,v,""]]
    for X in solutionList:
        if X[2] == "":
            print("Missing solution to question {} version {}".format(X[0], X[1]))
            return False
    return True


def build_soln_cover_data(msgr, tmpdir, t, maxMarks):
    """Builds the information used to create solution cover pages.

    Args:
        msgr (FinishMessenger): Messenger object that talks to the server.
        t (int): Test number.
        maxMarks (dict): Maxmarks per question str -> int.

    Returns:
        tuple: (testnumber, sname, sid, tab) where `tab` is a table with
            rows `[q_label, ver, mark, max_mark]`.
    """
    # should be [ [sid, sname], [q,v,m], [q,v,m] etc]
    cpi = msgr.RgetCoverPageInfo(t)
    spec = msgr.get_spec()
    sid = cpi[0][0]
    sname = cpi[0][1]
    # for each Q [q, v, mark, maxPossibleMark]
    arg = []
    for qvm in cpi[1:]:
        question_label = get_question_label(spec, qvm[0])
        arg.append([question_label, qvm[1], qvm[2], maxMarks[str(qvm[0])]])
    testnumstr = str(t).zfill(4)
    covername = tmpdir / "cover_{}.pdf".format(testnumstr)
    return (int(t), sname, sid, arg, covername)


def build_assemble_args(msgr, srcdir, short_name, outdir, t):
    """Builds the information for assembling the solutions.

    Args:
        msgr (FinishMessenger): Messenger object that talks to the server.
        srcdir (str): The directory we downloaded solns img to. Is also
            where cover page pdfs are stored
        short_name (str): name of the test without the student id.
        outdir (str): The directory we are putting the cover page in.
        t (int): Test number.

    Returns:
       tuple : (outname, short_name, sid, covername, rnames)
    """
    info = msgr.RgetCoverPageInfo(t)
    # info is list of [[sid, sname], [q,v,m], [q,v,m]]
    sid = info[0][0]
    # make soln-file-List
    sfiles = []
    for X in info[1:]:
        sfiles.append(Path(srcdir) / f"solution.{X[0]}.{X[1]}.png")

    outdir = Path(outdir)
    outname = outdir / f"{short_name}_solutions_{sid}.pdf"
    testnumstr = str(t).zfill(4)
    covername = srcdir / f"cover_{testnumstr}.pdf"
    return (outname, short_name, sid, covername, sfiles)


def main(testnum=None, server=None, pwd=None):
    msgr = start_messenger(server, pwd)
    try:
        shortName = msgr.getInfoShortName()
        spec = msgr.get_spec()
        numberOfQuestions = spec["numberOfQuestions"]

        outdir = Path("solutions")
        outdir.mkdir(exist_ok=True)
        tmpdir = Path(tempfile.mkdtemp(prefix="tmp_images_", dir=os.getcwd()))

        solutionList = msgr.getSolutionStatus()
        if not checkAllSolutionsPresent(solutionList):
            raise RuntimeError("Problems getting solution images.")
        print("All solutions present.")
        print(f"Downloading solution images to temp directory {tmpdir}")
        for X in tqdm(solutionList):
            # triples [q,v,md5]
            img = msgr.getSolutionImage(X[0], X[1])
            filename = tmpdir / f"solution.{X[0]}.{X[1]}.png"
            with open(filename, "wb") as f:
                f.write(img)

        # dict key = testnumber, then list id'd, #q's marked
        completedTests = msgr.RgetCompletionStatus()
        maxMarks = msgr.MgetAllMax()
        # arg-list for assemble solutions
        solution_args = []
        # get data for cover pages
        cover_args = []

        if testnum is not None:
            t = str(testnum)
            try:
                completed = completedTests[t]
            except KeyError:
                raise ValueError(
                    f"Paper {t} does not exist or otherwise not ready"
                ) from None
            if not completed[0]:
                raise ValueError(f"Paper {t} not identified, cannot reassemble")
            if completed[1] != numberOfQuestions:
                print(f"Note: paper {t} not fully marked but building soln anyway")
            # append args for this test to list
            cover_args.append(build_soln_cover_data(msgr, tmpdir, t, maxMarks))
            solution_args.append(
                build_assemble_args(msgr, tmpdir, shortName, outdir, t)
            )
        else:
            print(f"Building arguments for UP TO {len(completedTests)} solutions...")
            for t, completed in tqdm(completedTests.items()):
                # check if the given test is ready for reassembly (and hence soln ready for assembly)
                if not completed[0]:
                    continue
                # Maybe someone wants only the finished papers?
                # if completed[1] != numberOfQuestions:
                #     continue
                # append args for this test to list
                cover_args.append(build_soln_cover_data(msgr, tmpdir, t, maxMarks))
                solution_args.append(
                    build_assemble_args(msgr, tmpdir, shortName, outdir, t)
                )
    finally:
        msgr.closeUser()
        msgr.stop()

    N = len(solution_args)
    print("Assembling {} solutions...".format(N))
    with Pool(4) as p:
        r = list(
            tqdm(
                p.imap_unordered(_parfcn, list(zip(cover_args, solution_args))), total=N
            )
        )

    # Serial
    # for z in zip(cover_args, solution_args)
    #    _parfcn(z)

    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main()
