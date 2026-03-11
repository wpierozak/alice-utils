void rootlogon() {
    std::cout << "\n--- Configuring ROOT Environment ---" << std::endl;

    // 1. Tell Cling (the interpreter) and ACLiC (the compiler) where your headers are
    gInterpreter->AddIncludePath("include");
    gSystem->AddIncludePath("-Iinclude");

    // 2. Redirect all compilation artifacts to a "build" directory to keep folders clean
    // The 'true' argument tells ROOT to create the directory if it doesn't exist
    gSystem->SetBuildDir("build", true);

    std::cout << "------------------------------------\n" << std::endl;
}