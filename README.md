ვებჰუკი
მხოლოდ ახალი ფაილები რომ გაეშვას 
ჰეშის ან რილიზის დამატება ჯარის სახელში
ჯარ ფაილის შემოწმება თუ სწორია


- name: Checkout Build Repository
      uses: actions/checkout@v4

    - name: Checkout Schema Repository
      uses: actions/checkout@v4
      with:
        repository: 'your-org/schema-repo'
        path: 'external-schemas'
        fetch-depth: 0 # <-- CRUCIAL: Fetches all history so we can run git diff

    - name: Get Changed Schema Files
      id: changed-files
      run: |
        # Calculate changes between the current commit (HEAD) and the previous one (HEAD~)
        # --diff-filter=AM filters for files that were Added (A) or Modified (M)
        # grep matches only files ending in .cfg inside the schemas folder
        CHANGED=$(git -C external-schemas diff --name-only --diff-filter=AM HEAD~1 HEAD | grep '^schemas/.*\.cfg$' || true)
        
        if [ -z "$CHANGED" ]; then
          echo "No new or modified configuration files found."
          echo "HAS_CHANGES=false" >> $GITHUB_ENV
        else
          # Format the list into a single space-separated string for Python
          # e.g., "schemas/orders.cfg schemas/users.cfg"
          SPACE_SEPARATED=$(echo $CHANGED | tr '\n' ' ')
          
          # Save to environment variables
          echo "CHANGED_FILES=$SPACE_SEPARATED" >> $GITHUB_ENV
          echo "HAS_CHANGES=true" >> $GITHUB_ENV
          echo "Files to process: $SPACE_SEPARATED"
        fi

    - name: Set up Python
      if: env.HAS_CHANGES == 'true'
      uses: actions/setup-python@v5
      with:
        python-version: '3.x'

    - name: Install sbt CLI
      if: env.HAS_CHANGES == 'true'
      uses: sbt/setup-sbt@v1

    - name: Set up JDK and SBT Caching
      if: env.HAS_CHANGES == 'true'
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'
        cache: 'sbt'

    - name: Initialize sbt Configuration
      if: env.HAS_CHANGES == 'true'
      run: |
        mkdir -p project
        echo 'name := "delta-schema-jar"' > build.sbt
        echo 'version := "1.0.'${{ github.run_number }}'"' >> build.sbt
        echo 'scalaVersion := "2.13.12"' >> build.sbt
        echo 'sbt.version=1.9.8' > project/build.properties

    - name: Generate Scala Code
      if: env.HAS_CHANGES == 'true'
      # Pass the external repo directory followed by the list of changed files
      run: python generate_schemas.py external-schemas ${{ env.CHANGED_FILES }}

    - name: Compile and Package JAR
      if: env.HAS_CHANGES == 'true'
      run: sbt package
