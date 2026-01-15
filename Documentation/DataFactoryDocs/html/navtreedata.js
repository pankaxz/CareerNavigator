/*
 @licstart  The following is the entire license notice for the JavaScript code in this file.

 The MIT License (MIT)

 Copyright (C) 1997-2020 by Dimitri van Heesch

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 and associated documentation files (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, merge, publish, distribute,
 sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or
 substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
 BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 @licend  The above is the entire license notice for the JavaScript code in this file
*/
var NAVTREE =
[
  [ "CareerNavigator DataFactory", "index.html", [
    [ "CareerNavigator DataFactory Documentation", "index.html", "index" ],
    [ "DataFactory: Deep Dive Documentation", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html", [
      [ "1. Visual File Structure", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md14", null ],
      [ "2. Detailed Logic Breakdown", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md16", [
        [ "Phase 1: Input &amp; Cleaning (The Fuel)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md17", [
          [ "1. Input Source", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md18", null ],
          [ "2. Splitting Logic (IOHandler)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md19", null ],
          [ "3. Text Cleaning Logic (TextProcessor)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md20", null ]
        ] ],
        [ "Phase 2: Configuration (The Map)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md21", null ],
        [ "Phase 3: The Brain (Seniority Scoring)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md22", [
          [ "The Scoring Algorithm (Detailed)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md23", null ]
        ] ],
        [ "Phase 4: Building the Graph (Counting Logic)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md24", [
          [ "Logic A: Initialization (Setting up Buckets)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md25", null ],
          [ "Logic B: incremental Updates (The Loop)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md26", null ]
        ] ],
        [ "Phase 5: The Output", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md27", null ]
      ] ],
      [ "Summary of execution flow", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2DeepDive.html#autotoc_md29", null ]
    ] ],
    [ "Career Navigator DataFactory - System Documentation", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html", [
      [ "1. processor.py (The Orchestrator)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md32", null ],
      [ "2. utils/graph_builder.py (The Builder)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md34", null ],
      [ "3. utils/text_processor.py (The Miner / NLP Engine)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md36", null ],
      [ "3. utils/io_handler.py (The Logistics Manager)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md38", null ],
      [ "4. output/taxonomy.py (The Map)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md40", null ],
      [ "5. raw_jds.txt (The Raw Material)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md42", null ],
      [ "6. output/universe.json (The Final Product)", "md__2mnt_294D09184D0916D6C_2WORKSPACE_2CareerNavigator_2DataFactory_2psuedo.html#autotoc_md44", null ]
    ] ],
    [ "Packages", "namespaces.html", [
      [ "Package List", "namespaces.html", "namespaces_dup" ],
      [ "Package Members", "namespacemembers.html", [
        [ "All", "namespacemembers.html", null ],
        [ "Functions", "namespacemembers_func.html", null ],
        [ "Variables", "namespacemembers_vars.html", null ]
      ] ]
    ] ],
    [ "Classes", "annotated.html", [
      [ "Class List", "annotated.html", "annotated_dup" ],
      [ "Class Index", "classes.html", null ],
      [ "Class Members", "functions.html", [
        [ "All", "functions.html", null ],
        [ "Functions", "functions_func.html", null ]
      ] ]
    ] ],
    [ "Files", "files.html", [
      [ "File List", "files.html", "files_dup" ]
    ] ]
  ] ]
];

var NAVTREEINDEX =
[
"analytics__engine_8py.html"
];

var SYNCONMSG = 'click to disable panel synchronization';
var SYNCOFFMSG = 'click to enable panel synchronization';
var LISTOFALLMEMBERS = 'List of all members';