# CHANGELOG



## v0.8.2 (2023-09-24)

### Fix

* fix: Fix missing commas in PollPermissions list ([`9550a8f`](https://github.com/unipoll/api/commit/9550a8fc45b8c9917d0d790b0c7db1d8b3ddfad2))

### Unknown

* Merge pull request #64 from unipoll/development

fix: Fix missing commas in PollPermissions list ([`b38c3e2`](https://github.com/unipoll/api/commit/b38c3e21450fb22c1a7c11ab37e0fa3e5b536419))

* Update README.md

Updated badges ([`d808620`](https://github.com/unipoll/api/commit/d808620fb8ee01dbfdb23f67b9fb80335899d21c))

* Update README.md

Updated GitHub release Badge ([`5ea3db2`](https://github.com/unipoll/api/commit/5ea3db2cf05610045a36cfd186535b719a2966bc))

* Added PyPI Badge ([`a13d2e3`](https://github.com/unipoll/api/commit/a13d2e38794a4ec6b35700500c808f27c9560cff))


## v0.8.1 (2023-09-22)

### Build

* build: Excluded tests folder from distribution

Added Manifest.in and slightely changed project configuration to exclude tests folder from the distribution which was causing import error ([`7483101`](https://github.com/unipoll/api/commit/7483101608396a76ce691f21f36687166646d146))

### Fix

* fix: Fixed docker host ip

Changed host ip from 127.0.0.1 to 0.0.0.0 which was preventing connections from outside ([`0f8d89b`](https://github.com/unipoll/api/commit/0f8d89b86c377bea395096a87973ea3a7b6b43fd))

### Unknown

* revert: Removed minor flag

Removed option forcing updating minor versionh ([`0150b96`](https://github.com/unipoll/api/commit/0150b96486ef5605df011c105f652555c5268b8a))

* Update README.md

Changed API to api in badge links ([`5dc4129`](https://github.com/unipoll/api/commit/5dc41298148c3d7f8287c78cca0492dfbbf686a2))


## v0.8.0 (2023-09-21)

### Ci

* ci: Forcing minor version updated due to error ([`0cf6e85`](https://github.com/unipoll/api/commit/0cf6e85840b019f281114465dd4cf4ba1304b529))

### Fix

* fix: Add ref main to checkout actions ([`ae7753a`](https://github.com/unipoll/api/commit/ae7753afb0a6ece771728727f40325212cb413e6))


## v0.7.10 (2023-09-21)

### Breaking

* build: Moved source module to unipoll_api

BREAKING CHANGE: Changed project structure ([`49c2aa0`](https://github.com/unipoll/api/commit/49c2aa0983e58db1557b373e9e923f346723890b))

### Ci

* ci: Update releaes trigger ([`5f36871`](https://github.com/unipoll/api/commit/5f368718fb4f35dac24d21b9c430ca4730e3ed27))

* ci: Updated PyPI release job to use GiHub runner ([`070a60a`](https://github.com/unipoll/api/commit/070a60a20f041b42ac7e26e35e5ef8d63db2b4d3))

* ci: Deleted pypi workflow ([`bba484a`](https://github.com/unipoll/api/commit/bba484afd94baa3b8a1b49a4e1d64b7c69674a83))

* ci: Testing PYPI API Token with self hosted runner ([`cd283b2`](https://github.com/unipoll/api/commit/cd283b24e69dd76984ddb8bf84705019dc94a896))

* ci: Testing a different runner for PyPI release ([`57eb4a1`](https://github.com/unipoll/api/commit/57eb4a195ed63b8ba8a2a8f7fed9c06765248135))

* ci: Fixed the name of the workflow ([`15450fd`](https://github.com/unipoll/api/commit/15450fd4a66e313129ee2c280dd1e09bad7e8c5a))

* ci: Added separate workflow action for pypi release ([`0c8fee2`](https://github.com/unipoll/api/commit/0c8fee20c583ffc62ef0bd18872b4694f2f47d99))

### Feature

* feat: Added issue auto labeler workflow

The new workflow will automaticaly assign labels based on keywords in title ([`257beab`](https://github.com/unipoll/api/commit/257beab9225e43527ef5b81f5f0e721b775c3b85))

* feat: Added routes to update and delete polls ([`766fd63`](https://github.com/unipoll/api/commit/766fd63e8fb1f2c8c8b06fc2abe09a0be9575219))

* feat: Add actions to update and delete poll ([`6bc7310`](https://github.com/unipoll/api/commit/6bc7310c9aa9501090af6fab51aad6e3bfd12a9a))

### Fix

* fix: Fixed path to __version__.py ([`cc085db`](https://github.com/unipoll/api/commit/cc085db6f93fe04afd77837a209b0dcbd3765dd9))

* fix: TypeError: HEAD is a detached symbolic reference on PR

This is a general problem with CI services that checkout the repo by commit hash - because PSR has to create a new commit to update versions etc, it needs a branch to commit that to. ([`1e830dc`](https://github.com/unipoll/api/commit/1e830dcac912b85a2e4270944167715fa672b7a4))

* fix: Fixed branch name from dev to development ([`04a01b4`](https://github.com/unipoll/api/commit/04a01b46d91ef8b3bfbcc842dc29c4dfe017ee77))

* fix: Linting and checking validity of types ([`9d2bba3`](https://github.com/unipoll/api/commit/9d2bba3c932fd9d8833f06e3cc00eb21382388ca))

* fix: Changed username to user ([`83c18b7`](https://github.com/unipoll/api/commit/83c18b7f219b063584910368d8fb39df2a608ec3))

### Refactor

* refactor: Changed package structure for building distribution

Moved source module to unopoll_api module inside of src, added argparser to main and run functions, added entry point for the project, fixed pyproject.toml and Dockerfile, fixed all imports

closes #57 ([`63deb00`](https://github.com/unipoll/api/commit/63deb009995bf125c0bcd50115d2461fe2c6937a))

* refactor: Updated Poll Schemas naming

Added CreatePollRequest and UpdatePollRequest schemas, renamed Poll schema to PollResponse ([`afaf278`](https://github.com/unipoll/api/commit/afaf278210c981b9cee2855cfa264652a7ebbb90))

### Test

* test: Fixed pytest and tox issues for unipoll_api module

Added new file test-requirements.txt with deppendencies for tox, specified project layout for testing, removed redundant TestClient and cleaned up imports in the test files ([`6506d21`](https://github.com/unipoll/api/commit/6506d21c5b13bb2d9a1cd62726bf94e62ef01ab5))

### Unknown

* Merge pull request #63 from unipoll/development

Minor CI Updates ([`1c00df0`](https://github.com/unipoll/api/commit/1c00df05dab40a98c021c28bc262285f4d129427))

* Merge pull request #61 from unipoll/development

Development merged ([`42d40fa`](https://github.com/unipoll/api/commit/42d40fa8638f3179dfbbe6d1b8a7dbde61597319))

* Merge pull request #60 from unipoll/build

Updated Project Structure for PyPI release ([`53a06ca`](https://github.com/unipoll/api/commit/53a06cae2843eaa89b7413bbc51c8b08414d1613))

* Merge pull request #59 from unipoll/labels-workflow

feat: Added issue auto labeler workflow ([`e7cbf92`](https://github.com/unipoll/api/commit/e7cbf92113a8b315de9c565fb509145ac8d60dc6))

* Merge pull request #58 from unipoll/polls

Polls ([`93bb0d7`](https://github.com/unipoll/api/commit/93bb0d7e138a26f6babaa6728c1dd1d49052f22e))

* Merge branch &#39;main&#39; of github.com:unipoll/API ([`281450b`](https://github.com/unipoll/api/commit/281450b6684d35770f409d6acfc355e0094ce3b0))


## v0.7.9 (2023-09-18)

### Ci

* ci: Added checkout step to PyPI release job ([`2f61e81`](https://github.com/unipoll/api/commit/2f61e819562bb50d92d9ae5ae3a0684b21348610))

### Unknown

* Merge branch &#39;main&#39; of github.com:unipoll/API ([`ba57603`](https://github.com/unipoll/api/commit/ba57603162131f788b8bb7eefab86f6397cfe811))


## v0.7.8 (2023-09-18)

### Fix

* fix: Added matrix to pypi release step ([`629f080`](https://github.com/unipoll/api/commit/629f0807f3553e90d0f838fb680538904691ee27))


## v0.7.7 (2023-09-18)

### Build

* build: Changed name to unipoll-api ([`ffe4b80`](https://github.com/unipoll/api/commit/ffe4b80367cabed03a2bad0fe03c572c54aa014e))

### Ci

* ci: Updated PyPI release step ([`4bbf66c`](https://github.com/unipoll/api/commit/4bbf66cca421cbd731d95ccf354701d42646698d))


## v0.7.6 (2023-09-18)

### Ci

* ci: Fixed released condition for pypi job ([`e100810`](https://github.com/unipoll/api/commit/e100810683acdd2612681334645f8ec01af6fc45))

* ci: Added step to publish package to PyPI ([`441bd3a`](https://github.com/unipoll/api/commit/441bd3a05c00d06b9c40d66e8821e57f036de639))

* ci: Added test trigger on pull into main ([`df99d9e`](https://github.com/unipoll/api/commit/df99d9e7922fb2152609f48489fa2f463290aa5b))

* ci: Removed debug message from release step ([`aef429c`](https://github.com/unipoll/api/commit/aef429c353cd3529473f9df28299f3bfb5896031))

* ci: Added test as a requirement for release action ([`b91ff0a`](https://github.com/unipoll/api/commit/b91ff0ab4d3b79d5f79fe0210a7cf6eef904ae8d))

### Unknown

* Update README.md

Updated tests badge ([`d8ee875`](https://github.com/unipoll/api/commit/d8ee8750089f6f87905eab22b32a2edd0130a7f4))

* Update README.md

Changed color of version badge ([`9c0e7c7`](https://github.com/unipoll/api/commit/9c0e7c771f576bc691d1efe147cefa9602f625fb))

* Merge branch &#39;main&#39; of github.com:unipoll/API ([`a79a75b`](https://github.com/unipoll/api/commit/a79a75b1709c596c3f55dc90a90083604ea799a7))

* Update README.md

Added badges for GitHub release and Docker Image ([`5be3a4a`](https://github.com/unipoll/api/commit/5be3a4ad9c498e31ef9480f06ff0f935fe218325))


## v0.7.5 (2023-09-17)

### Ci

* ci: Updated actions

Added test job to release action, deleted docker action as it&#39;s moved to release, updated trigger for tests actions ([`93423ad`](https://github.com/unipoll/api/commit/93423ad6fd5e7ecc0d5493000df48164d631a229))


## v0.7.4 (2023-09-17)

### Ci

* ci: Added id to the release step ([`19bcc00`](https://github.com/unipoll/api/commit/19bcc00b744367631ada21cba0cf09a127c39a93))


## v0.7.3 (2023-09-17)

### Ci

* ci: Testing output variables without brackets ([`4d9894e`](https://github.com/unipoll/api/commit/4d9894eea496d84d90f09051ff64cb5e7ebe6cd1))


## v0.7.2 (2023-09-17)

### Build

* build: Removed package_data as not supported ([`46e9ea2`](https://github.com/unipoll/api/commit/46e9ea254bd25e6fb679b6704b954927a1a582fd))

* build: Updated pyproject.toml

Removed setuptools_scm, provided version manualy, updated email ([`67cd4a8`](https://github.com/unipoll/api/commit/67cd4a870af4457bc065323d3d3bca2ef7561d91))

### Ci

* ci: Updated release action

Added debug message to see the output variables, changed docker tag from output.tag to output.version ([`eb989c0`](https://github.com/unipoll/api/commit/eb989c054ce8dc8facd0fae7269902fb7bb1f0a4))


## v0.7.1 (2023-09-17)

### Breaking

* feat: Updated Polls

Updated polls document deffinition and schemas for polls and questions

BREAKING CHANGE: Added Polls ([`f2bc01d`](https://github.com/unipoll/api/commit/f2bc01d382f9c44f805cf4865880d8f18f233c18))

### Ci

* ci: Removed matrix value ([`48304f8`](https://github.com/unipoll/api/commit/48304f85d6803b7331f76b38ad4097c66ac5f592))

* ci: Updated release action

Added build command and forced patch version ([`08ede08`](https://github.com/unipoll/api/commit/08ede08687fd19aeeef35e7c20b908b93834332b))

* ci: Made jobs run sequentially ([`f912c06`](https://github.com/unipoll/api/commit/f912c06d2c0d7e0aa999875bfb41cd3853976d08))

* ci: Updated release actions

Added additional step to rebuild package manualy, added job to release Docker image using release output ([`937f218`](https://github.com/unipoll/api/commit/937f218af1a5ecd026d3ee699ee7fbaa94ea4f14))

### Feature

* feat: Added route to get Poll by id ([`56b12d8`](https://github.com/unipoll/api/commit/56b12d813afe59235e569d80903dbbc656e989d4))

* feat: Created actions to get questions and policies ([`6670083`](https://github.com/unipoll/api/commit/66700831281ac4b084a584ebaf3016a66e4e0b99))

* feat: Added model and permission dependencies for Polls

Added get_poll_model dependency to get a poll by id and verify it exists, and check_poll_permission to check if the current user has permissions to access the poll and perform requested actions ([`89eac3b`](https://github.com/unipoll/api/commit/89eac3b99de730bd555536297d7ff18ac9dc3da8))

* feat: Created permission class and parser for Polls

Created PollPermissions class from action file, added constants POLL_ALL_PERMISSIONS and POLL_BASIC_PERMISSIONS ([`6f3a866`](https://github.com/unipoll/api/commit/6f3a8665ae055e615d61870dd0f9518e2f9375f1))

* feat: Added exceptions for getting polls

Added exceptions PollNotFound, UserNotAuthorized, and ActionNotFound ([`e0e3a84`](https://github.com/unipoll/api/commit/e0e3a8402b47ba405f083dcff0671ca7db93cfbe))

* feat: Created QuestionList schema ([`486d2e2`](https://github.com/unipoll/api/commit/486d2e2b107a9bdbb24ae37e5ebf8df4be2ae4b2))

* feat: Updated schemas

Added public and workspace field to Poll schema ([`7669106`](https://github.com/unipoll/api/commit/76691065e78a4d308a4a2ef4b6b65b7cea3abe22))

* feat: Added public field to Poll documents ([`3d64638`](https://github.com/unipoll/api/commit/3d64638446ed5a5a1c086f7d62c473bd42f73699))

* feat: Added response scheme PollShort

Changed PollList scheme to exclude questions and policies fields ([`08a9645`](https://github.com/unipoll/api/commit/08a964560fdc57106995614b07960ef939310a7d))

* feat: Updated workspace resource

Added Polls definitions to workspace routes, schemas, and actions ([`e0f2611`](https://github.com/unipoll/api/commit/e0f26112d7b9ced0327c9833a6d563402cfff1f3))

* feat: Created Poll scheme ([`67bb557`](https://github.com/unipoll/api/commit/67bb5577a640009cda173c1f1d2dc51608ec8c2e))

* feat: Created Question scheme ([`c7e9b5d`](https://github.com/unipoll/api/commit/c7e9b5d5d040c2663db244f28dab27c7df09efa1))

* feat: Created document definition for polls ([`133e7e7`](https://github.com/unipoll/api/commit/133e7e7f5748914559c5c090dd9eda03921c2b31))

### Fix

* fix: Added question field to question model ([`d913b20`](https://github.com/unipoll/api/commit/d913b20b32f8112be74bc9f19981ce94749f76a4))

* fix: Added missing values when creating Poll document

Add public and policies fields when creating Poll document ([`d4d147d`](https://github.com/unipoll/api/commit/d4d147d1a75be80e2ab1413fc6453635d7b2ac79))

### Refactor

* refactor: Updated route and action to get list of polls

Changed workspace route and action to use PollShort scheme to response to exclude list of questions and policies from the list ([`aa23e32`](https://github.com/unipoll/api/commit/aa23e32abaa02c3477a117ee098288b6f62eed5f))

### Style

* style: Removed empty line at the beginning ([`cfad0ef`](https://github.com/unipoll/api/commit/cfad0ef5b4950775dcb26f2fd46f489a5a8cbdbc))


## v0.7.0 (2023-09-04)

### Build

* build: Added setuptools-scm package ([`7c2a914`](https://github.com/unipoll/api/commit/7c2a914082cf573c1b146d253827d1a63bb1626a))

* build: Updated the dependencies ([`0608158`](https://github.com/unipoll/api/commit/06081584660f479818c3858646785af1c00f3893))

* build: Deleted pytest.ini

Deleted pytest.ini, the config was moved to pyproject.toml ([`88874c5`](https://github.com/unipoll/api/commit/88874c59da1f2d2575c9a2d1f5a925c8d957e8b9))

### Ci

* ci: replaced semantic-release version from 8.0.x to 8.0.8 ([`329dafe`](https://github.com/unipoll/api/commit/329dafe248ec39dc68ea1fafac8ac15ab83939a5))

* ci: Added permisions to semantic-release action ([`ef15984`](https://github.com/unipoll/api/commit/ef159841af4aaf333e3de567f9e9f9153c612d1f))

* ci: Changed tests action trigger

Trigger tests action on pull requests into main branch ([`ebf3b66`](https://github.com/unipoll/api/commit/ebf3b6680220c063d8affba8da900b54cb2efb6e))

* ci: Updated semantic_release config ([`0e92f50`](https://github.com/unipoll/api/commit/0e92f505ce3d766e5547b228505dcf6be6cd89fb))

* ci: Added tag_commit option ([`a6276b9`](https://github.com/unipoll/api/commit/a6276b9e91ca6dc4535af2117a747d683338a8cf))

### Feature

* feat: Add coveralls action ([`48f6883`](https://github.com/unipoll/api/commit/48f68832a1da197ab817be64ee75c85a6b4424dd))

* feat: Added xml coverage report when testing ([`33a43e2`](https://github.com/unipoll/api/commit/33a43e227ff9850bd5bae1dff0f66bcd44c8eb0a))

* feat: Added exception for error when removing a member ([`b14b2c1`](https://github.com/unipoll/api/commit/b14b2c1c146730f9977cef189672aa483721486e))

* feat: Added schema for PATCH request to Update Workspace ([`0362849`](https://github.com/unipoll/api/commit/036284971ab5f9b4ff27b39c0b8afebbee73a763))

* feat: Added query params to GET Group request

Added query param include, to get policies and/or members of the groups, when calling GET Group request ([`ac5b739`](https://github.com/unipoll/api/commit/ac5b7399a89d94a4835e2c1a78e52202ab398a96))

* feat: Added the enpoints to get all possible permissions

Created route endpoints and actions for getting Groups and Workspace
permissions list

Closes #50 ([`738f59b`](https://github.com/unipoll/api/commit/738f59b7e469936c869181d5a0cb71f597f9e245))

* feat: Included Group open_router

Added open_router from Group routes to the app ([`ac70686`](https://github.com/unipoll/api/commit/ac70686c67fcc888a1668ac43f85134fbd9a2050))

* feat: Added enpoint to get list of all accounts ([`e42a3e4`](https://github.com/unipoll/api/commit/e42a3e404caa9b88d6de653c7a04dfa587b08415))

### Fix

* fix: Fixed build command for semantic-release ([`1f14bab`](https://github.com/unipoll/api/commit/1f14bab8ec9247effb7567e1d44866be40ef5c31))

* fix: Fixed repo name of semantic-release action ([`85fa9b1`](https://github.com/unipoll/api/commit/85fa9b1b21995cf18d059ac40c7864399af879f9))

* fix: Changed coverage file format to lcov ([`1f5a8bf`](https://github.com/unipoll/api/commit/1f5a8bf0cae553b36e196626396b140d249859c3))

* fix: Added path to coverage file ([`bb2da33`](https://github.com/unipoll/api/commit/bb2da33de044f2bd7c5644fb6a8033b6f2de6a55))

* fix: Fixed issue with mypy

Fixed issue with mypy not parsing BaseSettings type ([`d540f7f`](https://github.com/unipoll/api/commit/d540f7fa22d0602a9a2e9b00411a89982a336197))

* fix: Fixed issue with setuptools-scm ([`1a63883`](https://github.com/unipoll/api/commit/1a63883482d1a222bf06e0cb03d7573c09d7c4dd))

* fix: [BUG]: Functions return hashed passwords #52 ([`89f98ef`](https://github.com/unipoll/api/commit/89f98ef02b9bed1c28239bc39df8217e7ebdca0b))

* fix: Fixed issue with WorkspacePermissions ([`35b0e0a`](https://github.com/unipoll/api/commit/35b0e0a59d5153571646487d3c7e08b8146dde53))

* fix: Removed group field from Group Schema ([`873c048`](https://github.com/unipoll/api/commit/873c0488bc3dfad19adf051b6e1bb137c7539856))

* fix: Fixed bug when returning output of update policy ([`af13f6f`](https://github.com/unipoll/api/commit/af13f6ff72c6ead22f64d77eba06cbd70fdd3089))

* fix: Fixed error when removing members ([`2a20596`](https://github.com/unipoll/api/commit/2a20596b50bbb70226567d2b44333278be749f06))

### Refactor

* refactor: Deleted empty models directory ([`88913a0`](https://github.com/unipoll/api/commit/88913a04f2aa098d25660154628f41ba0d4a771e))

* refactor: Moved documents.py from model to src ([`7244b4a`](https://github.com/unipoll/api/commit/7244b4a940a683339ff692604f8d975027d7d34b))

* refactor: Removed empty fields from response schema ([`bb893cd`](https://github.com/unipoll/api/commit/bb893cd838d59c8979686c0292e32fd33e01d8b4))

* refactor: Changed description max length to 1000 ([`b82dbc2`](https://github.com/unipoll/api/commit/b82dbc272dd9efa562d21b6991a8313ce25fe227))

* refactor: Changed few test according to default permissions ([`32d513e`](https://github.com/unipoll/api/commit/32d513e4936ba10b96f2734ec60ec4fd665ac426))

* refactor: Tested Workspace and Group actions, minor fixes ([`eec6c74`](https://github.com/unipoll/api/commit/eec6c746dc16783512e0c69be01a61565a670baf))

* refactor: Renamed get_all_group_policies action

Renamed get_all_group_policies action to get_group_policies ([`4dc2b3c`](https://github.com/unipoll/api/commit/4dc2b3cd9ad5c87ddc583ae7ae3385900eff37ea))

* refactor: Renamed get_all_group_policies action

Renamed get_all_group_policies action to get_group_policies ([`4f65216`](https://github.com/unipoll/api/commit/4f652162dea01c81614ff6cc739cb16d25f618f0))

* refactor: Renamed get_all_group_policies action

Renamed get_all_group_policies action to get_group_policies ([`8ff77f1`](https://github.com/unipoll/api/commit/8ff77f15ba1871a41cc035e2932118e69c6920b6))

* refactor: Moved action to get all permissions

Moved action to get all permissions to a separate action file, so
getting list of permissions does not require a permission ([`5d24b40`](https://github.com/unipoll/api/commit/5d24b40ea8ce626da87d04809190f7f1ca24fa1c))

* refactor: Changed default permissions for new policies ([`2436c4d`](https://github.com/unipoll/api/commit/2436c4d2cf4e8d3da9a7ddcd1f0c2a7b071d598f))

### Style

* style: Code cleanup and reorganization ([`1c1ee52`](https://github.com/unipoll/api/commit/1c1ee5225bcc228d8148532ca3c94abcce5254cf))

* style: Ignore typing ([`d262c3b`](https://github.com/unipoll/api/commit/d262c3bcbae0814e1d9f2825301def0e294081e2))

* style: Cleanup, renamed few variables ([`3bdec3f`](https://github.com/unipoll/api/commit/3bdec3f9127dd3928fedbe6c9b7755d29241f1f4))

* style: Updated route description

Expanded GET workspace request descriptions, renamed Workspace_resources to query_params ([`d381846`](https://github.com/unipoll/api/commit/d3818467f75995dd20c3559d68250e6da1f3ec34))

### Unknown

* Update README.md

Added coverage badge ([`8d85ad4`](https://github.com/unipoll/api/commit/8d85ad4b630a3f3ef5276b74ef75046ed29ef6b3))

* Merge pull request #54 from unipoll/development

Development ([`b134f05`](https://github.com/unipoll/api/commit/b134f053e50fbed398f933336e40ed09e6624a24))

* revert: Replaced file argument to path-to-lcov ([`a603c1d`](https://github.com/unipoll/api/commit/a603c1dc6a6c54959f50d7d3b68db0df6b7667f4))

* Merge pull request #49 from unipoll/front-end

Updates for Front End ([`d45e8fc`](https://github.com/unipoll/api/commit/d45e8fc9b70eed6ef980af16d6cca64527fad98d))


## v0.6.1 (2023-06-30)

### Fix

* fix: Fix no tag issue ([`d0120cd`](https://github.com/unipoll/api/commit/d0120cd160650ea7e89ffba91c5499409683fbc3))


## v0.6.0 (2023-06-30)

### Ci

* ci: Updated setup config and changelog ([`c3a74b3`](https://github.com/unipoll/api/commit/c3a74b32be59b76a72f83a41d81e1d0fca098ce2))

* ci: Add upload to repository ([`aec6992`](https://github.com/unipoll/api/commit/aec699219665c51fba2e2e12f0ddc4bd868a11d5))

* ci: Added git installation before checkout ([`7f49834`](https://github.com/unipoll/api/commit/7f4983424a630063079fa7cafada1667e33b1125))


## v0.5.0 (2023-06-30)

### Ci

* ci: Updated release workflow ([`faeda92`](https://github.com/unipoll/api/commit/faeda92d79896285dafee74163a55b8fa748ef7d))

* ci: Specified branch for semantic-release ([`f93c0e8`](https://github.com/unipoll/api/commit/f93c0e8d42fd4bc7f59f168e3ac78c0b3fd9b102))

* ci: Added python-semantic-release ([`de1e39d`](https://github.com/unipoll/api/commit/de1e39d49c1dcd0f9bb0c74ddca834afa5714e14))

### Unknown

* Merge pull request #48 from unipoll/Development

Development ([`c654a93`](https://github.com/unipoll/api/commit/c654a93fb6058437c586bb2f8da8d3098f217912))

* Merge pull request #47 from unipoll/Development

Changed workflows to be dispatched manually ([`6cc8a19`](https://github.com/unipoll/api/commit/6cc8a195285a6f9fded8129670eb42d247291f3c))

* Changed workflows to be dispatched manually ([`649bc63`](https://github.com/unipoll/api/commit/649bc631df00c8d7bc5a5febc019efb46a090b56))

* Merge pull request #46 from unipoll/Development

Fixing Docker Buildx Issue ([`eade4f8`](https://github.com/unipoll/api/commit/eade4f82a248501c563426aba8f100088b7fd348))

* Closes #45 ([`de2eec7`](https://github.com/unipoll/api/commit/de2eec743856116b1340bb4e98e46f39c84f91c3))

* Merge pull request #44 from unipoll/Development

Config and verison update ([`108a6e0`](https://github.com/unipoll/api/commit/108a6e057f12481653aa4144be26da3d176a6575))

* Updated version ([`15c32d3`](https://github.com/unipoll/api/commit/15c32d3007124df7db1f55709968f8b0197fe0db))

* Merge pull request #42 from unipoll/Development

v0.7.42 Update ([`1b3ffde`](https://github.com/unipoll/api/commit/1b3ffdeb4b9980b791c72599268b6336fe307f6b))

* Added admin email and Fields for settings ([`b413dc0`](https://github.com/unipoll/api/commit/b413dc02c0b73d06caec620cc87d8ebc6b6936b1))

* Removed erroneous get_account_db() ([`81554fc`](https://github.com/unipoll/api/commit/81554fc61da32297500653a53b4d8de9b0aa7e56))

* Cleanup ([`3009f56`](https://github.com/unipoll/api/commit/3009f5639f98a3d2516962e2e00b7b3ab4514bed))

* Added workflow dispatch ([`24e11b5`](https://github.com/unipoll/api/commit/24e11b5c905651fb48087d91b5d6c15823d04e52))

* Changed release package to softprops/action-gh-release@v1 ([`86b1183`](https://github.com/unipoll/api/commit/86b1183bfafdce81676043b5ccc82f4a1cf155d8))

* Fixed the runner issue with release workflow ([`de79855`](https://github.com/unipoll/api/commit/de79855dbc5f7def670aa101291e021b9967607b))

* Fixed issue with missing build module ([`52feb68`](https://github.com/unipoll/api/commit/52feb684ed93df0c537d30f90d6db19cb28f918c))

* Updated dependencies ([`bfb6a47`](https://github.com/unipoll/api/commit/bfb6a473e5c66c067410ada728676dfe0dbba26c))

* Fixed Runner name ([`a162d81`](https://github.com/unipoll/api/commit/a162d81e4e3c36a05a55650d3b6c8465722c5332))

* Merge remote-tracking branch &#39;origin/main&#39; into Development ([`e498f11`](https://github.com/unipoll/api/commit/e498f115ffd7e7c35ce01a0ab75af86a38b28c65))

* Changed runner ([`c502801`](https://github.com/unipoll/api/commit/c502801412a4d1de2ba402b67bfc04e072d9cb07))

* Added workflow to deploy docker images on release ([`6aee500`](https://github.com/unipoll/api/commit/6aee500c1e2da6eecec0700596575f070607078c))

* Created docker file ([`11618e3`](https://github.com/unipoll/api/commit/11618e31b1220733b539d8e8a5b4a7ea8fbe4823))

* Fixed flake8 and mypy issues ([`77c6cd0`](https://github.com/unipoll/api/commit/77c6cd0c04348872e9721be35cdb50f36d4223f4))

* Fixed spelling issues and print statements ([`1b8ff7b`](https://github.com/unipoll/api/commit/1b8ff7b4e8ffde3f7aae59164dbc0feb45ce90ff))

* Changed secrete to use settings from config
Added Client ID to settings ([`f7a878e`](https://github.com/unipoll/api/commit/f7a878e54638b7f5e66211ce14a020b7035b7b3d))

* Specified typing ([`4aaac46`](https://github.com/unipoll/api/commit/4aaac46f87a6d0eb2c8d99175151a099919f803c))

* Changed return to Group instead of GroupShort ([`9c30de8`](https://github.com/unipoll/api/commit/9c30de817406dff65db4b6a9ec79d6016c8915c0))

* Moved access token model, update auth response ([`2f79bd7`](https://github.com/unipoll/api/commit/2f79bd719d9cdb7a3167d27b0a0c1470d3787734))

* Added query params to get_workspace endpoint ([`9bfe492`](https://github.com/unipoll/api/commit/9bfe4923f189ecf09a8b340baf080090b2c6ac3e))

* Added endpoint for postman to refresh tokens ([`c18219c`](https://github.com/unipoll/api/commit/c18219cafc48d5695f47eee0187ac6de9c6315f1))

* Updated delete_account to remove access token ([`4e0685f`](https://github.com/unipoll/api/commit/4e0685feec3b6d708326a253b75f5407432353ef))

* Merge pull request #41 from unipoll/test_tox

Fixed issues to pass tox testing ([`7b0a535`](https://github.com/unipoll/api/commit/7b0a535a8db9384e3e1f2813c8747ff56b9c9870))

* Fixed mypy errors ([`a3dbb9c`](https://github.com/unipoll/api/commit/a3dbb9ce4f03b07c5493672f6f663a68d4add0e7))

* Removed check for untyped function definitions ([`bde8ee0`](https://github.com/unipoll/api/commit/bde8ee098ece21e043b0933df2a64337eda613cf))

* Fixing typing errors from mypy ([`8f0f3d7`](https://github.com/unipoll/api/commit/8f0f3d7d3b715ad84bf59e6a537f41f766bc9f72))

* Cleanup ([`f1accd4`](https://github.com/unipoll/api/commit/f1accd446c5fc831ae191ea9cd740f29a75a7150))

* Dictionary ([`38f360f`](https://github.com/unipoll/api/commit/38f360f24a3e51fbcf9098b0228f5c957b42bc3c))

* test workflow on commit ([`60b3bee`](https://github.com/unipoll/api/commit/60b3bee99f488a6ba6a1154c6a859f4a9d697f15))

* renamed workflow ([`c88b0c3`](https://github.com/unipoll/api/commit/c88b0c3f991e973a0528075c91120ee195a80385))

* testing tox ([`2f985fc`](https://github.com/unipoll/api/commit/2f985fc42e8cd6f436b142fd1ea6ef983a2fbe01))

* Debugging action runner ([`43e4a3a`](https://github.com/unipoll/api/commit/43e4a3a44f2c4e306abdde5326029bd912075329))

* Remove python3.10 as it does not pass the tests ([`ebe0900`](https://github.com/unipoll/api/commit/ebe0900c30cf04e90bd7b0152f903dc0a76c6399))

* Cleanup ([`b77224b`](https://github.com/unipoll/api/commit/b77224b3f45fc0eb59d4fd2493e6b11a6e5ac65b))

* flake8 ([`65e1169`](https://github.com/unipoll/api/commit/65e11696795becb2be72ca270d13b55514438ce2))

* Changed load order ([`839a3db`](https://github.com/unipoll/api/commit/839a3db2d92cd55dd8cd973d60c41354b17df399))

* Fixed issue with accounts router ([`0e6477d`](https://github.com/unipoll/api/commit/0e6477d2a0675cbc20ea6be79114c36234260bc8))

* renamed arc runner ([`54b531f`](https://github.com/unipoll/api/commit/54b531f95f4dfe3f595a0183c94f952d74736978))

* Testing arc-runner-set ([`78ad1be`](https://github.com/unipoll/api/commit/78ad1be996d17f160fe83f4c301684d1ecf02299))

* Added app config and updated app version ([`5d51243`](https://github.com/unipoll/api/commit/5d51243b971652b1aa216ae0686d49a63631be2b))

* Run tests on pull requests ([`dabd85c`](https://github.com/unipoll/api/commit/dabd85cf7272ca7554563d9661072b47baf3b5bb))

* Merge pull request #39 from unipoll/authentication

Authentication ([`3137530`](https://github.com/unipoll/api/commit/3137530d64c68174de0a6d17850577bc57f62d57))

* Merge pull request #38 from unipoll/group_testing

Updated Group Tests ([`ae188c3`](https://github.com/unipoll/api/commit/ae188c3febfa24ef33b501ae31dc4246c73c30f1))

* Merge branch &#39;websockets&#39; into authentication ([`060dfe7`](https://github.com/unipoll/api/commit/060dfe77cac4a0ecfafe0ddbcb38ec9e17cb6fd2))

* Separated the code into separate files ([`726a17d`](https://github.com/unipoll/api/commit/726a17d626e26cdaef7ddbf4eea8321137cf3fbd))

* Added endpoint and logic to refresh token ([`60b26e4`](https://github.com/unipoll/api/commit/60b26e4733955bc7daf1c8d56014a609ed5be3cf))

* Added custom strategy for authentication ([`6d812b0`](https://github.com/unipoll/api/commit/6d812b0c90a898b7dd6978359835eb032d2eba18))

* Cleaned up imports ([`043c2e2`](https://github.com/unipoll/api/commit/043c2e2d1a60380d6207741a12697ad32143cf13))

* Testing GH Actions ([`bce7e16`](https://github.com/unipoll/api/commit/bce7e16d4d9072f41375a866767712c855a6a899))

* Added cleanup ([`4992d86`](https://github.com/unipoll/api/commit/4992d86cfc8cf187c3dc3f7acec348d34151fcbd))

* Fix issue with tox-gh-actions ([`b1c5cf2`](https://github.com/unipoll/api/commit/b1c5cf234e8b960d4a409a6c4d906fd14156973e))

* Add option to suppress pip warning about running as root ([`2431351`](https://github.com/unipoll/api/commit/2431351d66c06f3a837e6b578465dedc98855edf))

* Fixed issue with PyJWT version ([`021a0c2`](https://github.com/unipoll/api/commit/021a0c24288a2b0c9492b1f974f00f797c68bee7))

* Updated tests action to use self-hosted runner ([`71cc8c8`](https://github.com/unipoll/api/commit/71cc8c8e1a5a8d52ff6522941662491d6e56ce7f))

* Added WS router ([`a8e7a70`](https://github.com/unipoll/api/commit/a8e7a700ca3d1f40ca1f64631c1584d50e80df87))

* Added Login route to return correct OAuth body
Moved imported routers to the separate file ([`f446650`](https://github.com/unipoll/api/commit/f44665000b7e6a8a6087658e17839f5fda5b2236))

* Added the default WS endpoint with dependencies
Added dependencies to check if token or cookies were supplied ([`3482215`](https://github.com/unipoll/api/commit/34822158b6c52c6b10a904cfbfbabaa93858b1ce))

* Added WS manager ([`401ef6a`](https://github.com/unipoll/api/commit/401ef6a8004600209774136bfaefbd39bcd8df17))

* Fixed all tests in group testing ([`0eb4437`](https://github.com/unipoll/api/commit/0eb4437059d4cfd5eab194e8a4da47233a9cc8ac))

* Fixed issue with fetching group links ([`f1a9f7b`](https://github.com/unipoll/api/commit/f1a9f7b179df9f2aff3fdd8541cdf1143e391b3d))

* Fixed endpoint naming,
Added route to get all policies,
Added route to delete members ([`afbb4a1`](https://github.com/unipoll/api/commit/afbb4a127677234569615c5165b9e41a3b6d311a))

* Added action to get all policies
Replaced action to set policy ([`699b203`](https://github.com/unipoll/api/commit/699b203d8799428c3434a1726905c41fa1546ab2))

* Cleaned files, stylistic ([`bd5e4e0`](https://github.com/unipoll/api/commit/bd5e4e047ac1b54bd553c6148815236512ecc456))

* Removed redundant print statements ([`e85c142`](https://github.com/unipoll/api/commit/e85c14276c928b6bbc65e83d0da265b4947211eb))

* Fixed status code ([`cf70e24`](https://github.com/unipoll/api/commit/cf70e245b5f41c450e95fa57aa80228f5982bb0f))

* Updated group testing ([`1d6cb74`](https://github.com/unipoll/api/commit/1d6cb74b4b0e11553f9eb2427e278fe181cc8ca3))

* minor stylistic changes ([`316cad9`](https://github.com/unipoll/api/commit/316cad9e226bf987f760c1cff0e4f77c5e621e6b))

* Added tests to Get all Policies, Set Permissions, and Delete Workspace ([`5483388`](https://github.com/unipoll/api/commit/548338845463a6f9b23d612bc02889b29351961f))

* Removed deprecated code ([`17a08f5`](https://github.com/unipoll/api/commit/17a08f515591274ac3b761f77713b97f10a55414))

* minor stylistic changes ([`5db228a`](https://github.com/unipoll/api/commit/5db228a7ef53b71eb0d6f44569e73d472814ff95))

* Added dependency to get and return account ([`69bd3cd`](https://github.com/unipoll/api/commit/69bd3cda4c5df33f6a4298fe00ae20bd2b720fbe))

* Updated route to delete current active user
Replaced default route to delete account by id ([`dada11f`](https://github.com/unipoll/api/commit/dada11f68ce4109650ca49a7644d1b67fe7ace7e))

* Renamed GET all_policies to GET policies ([`2512257`](https://github.com/unipoll/api/commit/2512257792aadc6d24176a6e42e4d4cd748f8d0a))

* minor changes ([`7acb080`](https://github.com/unipoll/api/commit/7acb0808d8cba6daf26dedd81274609ad436e4ac))

* Python version changed ([`c66246a`](https://github.com/unipoll/api/commit/c66246a4944209bf71fd85b712515fcf471e5ed7))

* Minor changes ([`1204244`](https://github.com/unipoll/api/commit/120424482b14b0af839dfe55ecbd24e4c35cd219))

* Added optional field for specifying Account ID ([`b9812b6`](https://github.com/unipoll/api/commit/b9812b6a7a64750739c4ffc198bbc43427911235))

* Added remove_member method to resources ([`c9ee950`](https://github.com/unipoll/api/commit/c9ee9505ab4896dbcdf9a345280fffbd53390c32))

* Changed Delete action to remove residual data ([`b52067a`](https://github.com/unipoll/api/commit/b52067a01e6eefb3f47e2f5e4399786a538846b2))

* Fixed set_workspace_policy ([`e9f0ad4`](https://github.com/unipoll/api/commit/e9f0ad4101b3f58746eaf3dfddbd404b803cf8eb))

* Merge branch &#39;workspace_testing&#39; of github.com:mike-pisman/PollingAPI into workspace_testing ([`e38fcb4`](https://github.com/unipoll/api/commit/e38fcb4084d12527b16b79c0d28c87c64ae23e7e))

* Added second workspace for testing
Added test to update workspace info with duplicate name
Added cleanup after tests ([`936d90b`](https://github.com/unipoll/api/commit/936d90b0aee7c726c58abc2df35a467152f9dbf7))

* Fixed wrong error code on Not Found Exception ([`fb0a6a3`](https://github.com/unipoll/api/commit/fb0a6a3528c62e2d4a42567a3b349d2a4dcca24b))

* Added policy deletion to delete workspace action ([`6946031`](https://github.com/unipoll/api/commit/69460317d4dc0e52e057ecd7d4b8c030de6ad7ec))

* Fixed status code for workspace deletion ([`fef2522`](https://github.com/unipoll/api/commit/fef2522018969454789c2e3b0769d509575a8e9a))

* Update README.md

fixed link to wiki ([`e25ecde`](https://github.com/unipoll/api/commit/e25ecde530c4073d6f928845febad98ac3f96c52))

* Update README.md

fixed link to wiki ([`600f1b2`](https://github.com/unipoll/api/commit/600f1b29b3d99f66fa647a7705033e5e0550a249))

* Created workspace tests
Coverage: action 46%, routes 57%, exceptions 77% ([`1e3066e`](https://github.com/unipoll/api/commit/1e3066e77129099b4d8464539ff618398bb64a69))

* Created file to test permissions ([`57bb3ac`](https://github.com/unipoll/api/commit/57bb3acf469a3abed84987afc068393f2f88ceaf))

* removed requirements_dev ([`d1f6788`](https://github.com/unipoll/api/commit/d1f67880da8d321891b04e749e3079a0a80a6960))

* Updated  requirements ([`f645cf6`](https://github.com/unipoll/api/commit/f645cf66b3ee2ff48ded708557a56e84455b5c52))

* Removed deprecated debug flag ([`87ff011`](https://github.com/unipoll/api/commit/87ff011443ebf709e5d4fd479c9fa32e7ba0904a))

* Changed group tests order to run after workspace tests ([`d6f0b0a`](https://github.com/unipoll/api/commit/d6f0b0a414cdbcbd22c91ab424a00feac3a5f275))

* Update check_workspace_permission to check if user id superuser ([`73602a6`](https://github.com/unipoll/api/commit/73602a6601cd24a7e07ae98c8b7e5f80bb2c4e85))

* Updated tests for Account(previously test_1_user) ([`2dfe1d7`](https://github.com/unipoll/api/commit/2dfe1d73b47dfde149ec76993eb4aebe831d8654))

* Updated version ([`a2add49`](https://github.com/unipoll/api/commit/a2add49f51c6b643218f241d1282c24fbd472e57))

* Moved List of document models to mongo_db.py
Renamed get_user_db to get_account_db
Moved create_link function to models/documents.py ([`7d45916`](https://github.com/unipoll/api/commit/7d459168de6e05cfa837842712f14fe4a6518049))

* Added account router
Fixed naming for imported routers
Renamed user into account
Moved List of document models to mongo_db.py ([`27c144a`](https://github.com/unipoll/api/commit/27c144a9f888b884cfa2ed1d176d9e6622e03691))

* Added database strategy for storing access tokens ([`81f467e`](https://github.com/unipoll/api/commit/81f467eeec8b9cc75ca5a82beef1cebe63fe5a50))

* Added recursive permission lookup through all nested groups
Added constants for default permission ([`9130d4e`](https://github.com/unipoll/api/commit/9130d4edebf8b806d25b02f8ad6b9b06f6f00d8d))

* Added PolicyOutput, PolicyList schemas
Added optional permissions field to PolicyShort
Added optional field policy_id for PolicyInput ([`2732830`](https://github.com/unipoll/api/commit/27328305363b4ba7608f82dcb320356024caa0de))

* Added Member, AddMembers, MemberList schemas
Created new member schemas in separate file schemas/members.py ([`8b6fd5a`](https://github.com/unipoll/api/commit/8b6fd5adce4ee5e930f797dacbf1d598c992d4c1))

* Removed deprecated member schemas ([`c5df2f0`](https://github.com/unipoll/api/commit/c5df2f0e20eed84d7efab70406d189136ec0fd1f))

* Removed deprecated member schemas
Removed regex filter for names ([`cd5600b`](https://github.com/unipoll/api/commit/cd5600bc6f0579ec915e80513bc65e6ad3bf5746))

* Fixed missing last name ([`10d42c8`](https://github.com/unipoll/api/commit/10d42c832db122af674c5862faefb6b74e1f5931))

* Added delete_members, get_all_workspace_policies endpoints
Modified endpoints to return HTTP Exceptions in case of catching APIExceptions
Change updating method for workspace from PUT to PATCH ([`6f175d7`](https://github.com/unipoll/api/commit/6f175d7ea68d9e8108b03449a8d4b5aeda8d0414))

* Modified all endpoints to return HTTPException on error(APIException) ([`5e3bcb6`](https://github.com/unipoll/api/commit/5e3bcb6e824847cdeb35627550247f943cfa3838))

* Replaced old routed definition with new format
Removed GET {user_id}/groups (deprecated)
Modified delete_user to use action delete_user and follow general format ([`61afe4b`](https://github.com/unipoll/api/commit/61afe4b7dfad29b0058f531ca43d736c138fe92a))

* Expanded name field to 50 characters
Added boolean Save option to add_member method
Fixed issue with wrong id type @65 ([`09b5e47`](https://github.com/unipoll/api/commit/09b5e473d6587f8ef8a0537ded0c294bac73790e))

* Modified AddingExistingMember exception to use APIException class ([`89f3375`](https://github.com/unipoll/api/commit/89f33758d78b56d4699e06335c6b0db3a102360b))

* Added PolicyNotFound exception
Created Policy Exception file exceptions/policy.py ([`6e8c776`](https://github.com/unipoll/api/commit/6e8c776c9a4554eaa109ecce176b8ca6189700b9))

* Removed deprecated UserNotInGroup, UserAlreadyExists
Reworked UserNotAuthorized, AddingExistingMember to use APIException ([`0898540`](https://github.com/unipoll/api/commit/08985406623519cc32bb8827225565c88d749307))

* Added ErrorWhileDeleting exception
Replaced deprecated AccountNotFound with Resource exception ([`3a41dc8`](https://github.com/unipoll/api/commit/3a41dc8ece6cfd561554085b0a8f435209ffc0f5))

* Converted exceptions from HTTPException to custom class APIException ([`7711dd5`](https://github.com/unipoll/api/commit/7711dd526b1f958870d53a6454afbc9648e468a6))

* hid __init__ files, ([`35cd326`](https://github.com/unipoll/api/commit/35cd3262a8aab48f246116183c82b9e59075256d))

* Renamed get/add permission  to get/add policy
Added action to get list of all workspace policies
Replaced default permissions with constants from Permissions.py
Added MemberList schemas for get/add members
Fixed get_workspace_members output schema ([`ba40661`](https://github.com/unipoll/api/commit/ba4066113d3568f9aada6d3641b6e4886953fa48))

* Removed deprecated dependency method ([`0552ccb`](https://github.com/unipoll/api/commit/0552ccbe2fc22c9222f5703e4aad3f039083b059))

* Added account_id query to get/post_permission
Added MemberList Schemas to get/post_members ([`bf1b856`](https://github.com/unipoll/api/commit/bf1b856ad67ce991b17b19ffeece48d2287e7d00))

* Moved account_manager ([`127898b`](https://github.com/unipoll/api/commit/127898b67776edbed0c8530c8c1c2bfee3fd991f))

* Remove settings.json from staging area ([`2dad989`](https://github.com/unipoll/api/commit/2dad9891b6c95474726c0b29ff86b2ce0c7e973d))

* Added Permissions, finished Rework ([`3b5e736`](https://github.com/unipoll/api/commit/3b5e73654fef2ba8f4f022ec1cdf8d8a807a3fee))

* cleanup ([`57566b6`](https://github.com/unipoll/api/commit/57566b6ba43d2be5ff7e8d2653f51c1f12c30913))

* Created dependency module ([`ae1ef10`](https://github.com/unipoll/api/commit/ae1ef106c78af8e6d9cb1136bdfe5a09829257ba))

* Renamed user into account ([`99b135a`](https://github.com/unipoll/api/commit/99b135a013da9b90d7a0bb0907d9ce81257bc912))

* Moved all Document models into one file ([`ac39ca5`](https://github.com/unipoll/api/commit/ac39ca557ca8a42ac1cd9a293082ae3972e3c8cf))

* Added policy and permission (untested) ([`9f2d06b`](https://github.com/unipoll/api/commit/9f2d06b4981ce8f9887f4c9a96a9dff80dec5079))

* Hid directories not related to project ([`8a6d8a1`](https://github.com/unipoll/api/commit/8a6d8a1f628d7872fbc69f3f21dc063f82a838a3))

* Added group router ([`d62a4d1`](https://github.com/unipoll/api/commit/d62a4d1424bea1e8503643e04f4e6d124c18a106))

* Added basic CRUD and CR for members ([`6487115`](https://github.com/unipoll/api/commit/6487115c61ada5d2fafd874573ee1e1129c7f264))

* Added basic CRUD, CR for workspace members/groups ([`922278f`](https://github.com/unipoll/api/commit/922278fe3b5319a90e67752adbd6879ddb1f4497))

* Added ErrorWhileDeleting exception ([`1f90189`](https://github.com/unipoll/api/commit/1f90189d4df2bc28d3b8b0ae86c57babd9ac85e7))

* Created actions to get/add members to workspace ([`13d6128`](https://github.com/unipoll/api/commit/13d6128d2adcb6fdd5db5b12eeecb3e9ae02dd4f))

* Changed list_groups route to use get_user_groups() ([`a5615cb`](https://github.com/unipoll/api/commit/a5615cbc7162c80c85a03c0ed15aafbfcc6bc274))

* Fixed get_user_groups();
Updated create_group() to add group to workspace ([`ba56021`](https://github.com/unipoll/api/commit/ba56021cc301f659a7c2c0c526dde68fe321478a))

* Added action to create groups ([`eb8d747`](https://github.com/unipoll/api/commit/eb8d74729a8b8b1f407f0b7b4c0e833bc5e7e588))

* Update import naming ([`3a77b93`](https://github.com/unipoll/api/commit/3a77b93592caa0779fc61497273d2212f89f8f69))

* Renamed UserRead Schemas ([`96d30df`](https://github.com/unipoll/api/commit/96d30df48c926150f7a151e757bad20f4131c55a))

* Renamed and updated output schemas for groups ([`cd46a88`](https://github.com/unipoll/api/commit/cd46a8887dd0136942e5bf74acee2aa04686167f))

* Removed group list from user model ([`7de58d8`](https://github.com/unipoll/api/commit/7de58d8be1b82a736b01e81ce879b9ad12f89a2a))

* Move route to list groups into workspace router ([`a1af1db`](https://github.com/unipoll/api/commit/a1af1db44e7d49435e6f1939ddcd3bb363331d66))

* Update group model to use links
Added method for adding user link ([`2bc7c78`](https://github.com/unipoll/api/commit/2bc7c78843597d3e01cbf2a9d70e22c19d68b360))

* Added ids to workspace output schemas ([`bb525b7`](https://github.com/unipoll/api/commit/bb525b74de2d5c92e74c614b14abbe311270d03c))

* Added group actions to GET list of groups ([`154a26e`](https://github.com/unipoll/api/commit/154a26e43c42845907e83728b442372cd10f1cb0))

* Added a list of group links to Workspace model ([`b626226`](https://github.com/unipoll/api/commit/b6262265b2a03842e607998faa61e4e0757bfeae))

* Created an abstract class for exceptions ([`e5eba2d`](https://github.com/unipoll/api/commit/e5eba2db44bfc7e55b8864274aa7bdaa62c2256e))

* Added Workspace router to the project
Added Workspace document model to the database
Added set_active_user Dependency to save user in the context
Temporary removed user and group routers from the project ([`a27d8f8`](https://github.com/unipoll/api/commit/a27d8f84a105ad6c23e40364d241aaeef8f20bae))

* Added a ContextVar for current user ([`bd6c1cc`](https://github.com/unipoll/api/commit/bd6c1ccb29739a34eed3ada092d6440befe2efe1))

* Added bson to the dictionary ([`b6fec56`](https://github.com/unipoll/api/commit/b6fec565a05251bad11052746b551295bf364b62))

* Added schema, route, and action to create a  workspace ([`257ae4d`](https://github.com/unipoll/api/commit/257ae4ded011d6a3a3fe72c57e386acfe2e4a0f2))

* Added exceptions for workspace creation ([`7399fe0`](https://github.com/unipoll/api/commit/7399fe0947a4aca9657a2552dc10e60cb729ed7b))

* Added GET route to list workspaces ([`2dbc221`](https://github.com/unipoll/api/commit/2dbc221e84af6f48ee3f279856488f99dc933238))

* Created actions to get a list of workspaces ([`c768bb9`](https://github.com/unipoll/api/commit/c768bb963e248470f0a62fddc3efc0137a0cb999))

* Created schemas for reading workspaces ([`d34ce93`](https://github.com/unipoll/api/commit/d34ce933123479d13f08309be73cb821f870a57f))

* Created WorkspaceID schema ([`bd4fa0c`](https://github.com/unipoll/api/commit/bd4fa0cb51dac56195553699a94cf4967bcd8bbb))

* Created method to add member to the workspace list ([`2e299df`](https://github.com/unipoll/api/commit/2e299df5841acf473fdc69038252edc347556ff9))

* Created Workspace model ([`81eb993`](https://github.com/unipoll/api/commit/81eb993011bd2cf0c43066045cbfee145dbee587))

* Initial version of release workflow ([`e8fa47c`](https://github.com/unipoll/api/commit/e8fa47c52135b8f2284e92731afddca4196a8288))

* Initial version of postman workflow ([`0334c4a`](https://github.com/unipoll/api/commit/0334c4a55599a7b6248f32ee4b5976b19ee84eb3))

* Removed extra checkout step ([`0568fe8`](https://github.com/unipoll/api/commit/0568fe87b94c06a848af85b1d0fda51f1f576bbd))

* Added links ([`ea3a975`](https://github.com/unipoll/api/commit/ea3a9757acfb6fba8161cc90350db6c56d239ea4))

* Update ([`9a03d12`](https://github.com/unipoll/api/commit/9a03d12c812f74a87d9d52e7c287551c30a08edc))

* Added 0.0.4 documentation ([`6e40ed2`](https://github.com/unipoll/api/commit/6e40ed27b53523f594175a353d62e2b183563127))

* Added 0.0.5 version ([`8cd42fc`](https://github.com/unipoll/api/commit/8cd42fca446e360e448ba6bb5e60664a7ffcbd47))

* Merge pull request #30 from mike-pisman/Testing

Testing ([`e5ec36a`](https://github.com/unipoll/api/commit/e5ec36ad7f838f64bab5b57e65c547eb9f176f53))

* Merge branch &#39;Development&#39; into Testing ([`7815e67`](https://github.com/unipoll/api/commit/7815e6786a79923731b0d2fe2bc0e7d35b2aa075))

* Fixed pyproject.toml ([`11b1e14`](https://github.com/unipoll/api/commit/11b1e14844daae193ddebc84d24f6e13775fad55))

* removed redundant print statement ([`293ee4c`](https://github.com/unipoll/api/commit/293ee4c93abb553acb03ad81cdc3fd5755a58fdc))

* Update test to delete user using endpoint /users/me ([`a3371ab`](https://github.com/unipoll/api/commit/a3371abee27872bc034c6d02fdbb355922730ebe))

* Fixed mypy issues ([`96f9bbc`](https://github.com/unipoll/api/commit/96f9bbcb4d5fbf94e5cb00493b8bf8d8a635fde0))

* Added dynamic version setup through config file ([`3db2b8f`](https://github.com/unipoll/api/commit/3db2b8ff9ecc1860af1427ecf99309b3e5222874))

* Removed trailing space ([`3fc468b`](https://github.com/unipoll/api/commit/3fc468b17af33e2e43fffc7db1a7d2e65f70103e))

* Merge pull request #29 from mike-pisman/Groups

Groups ([`43a551a`](https://github.com/unipoll/api/commit/43a551ab3a78d3627963cf9bd5bf1f555cd50d05))

* Added comments ([`92ba323`](https://github.com/unipoll/api/commit/92ba323086ed9a863a08e98104d92b789c65e8e9))

* Styling ([`47f3032`](https://github.com/unipoll/api/commit/47f30327cd8f095da9715186a81ec4a6bea90ba9))

* Replaced PydanticObjectId with UserID ([`d9b776d`](https://github.com/unipoll/api/commit/d9b776dfb38299cec317c3d7a268e9c694997ff3))

* Styling ([`13c509f`](https://github.com/unipoll/api/commit/13c509ffa6636f32fb5061b8ed655aa2cdfb8e1b))

* Added type check ([`e19cbc9`](https://github.com/unipoll/api/commit/e19cbc939e7af859d8c983680ee42c23cdcfed3d))

* Fixed error with updating the role (tested) ([`1cf764d`](https://github.com/unipoll/api/commit/1cf764d16c6572c1c72cb583d777b24c22a8b2cc))

* Replaced PydanticObjectID with UserID/GroupID ([`50523ca`](https://github.com/unipoll/api/commit/50523cad2c8208fd24bda751826a99b3e25f17f3))

* Added comments ([`bd32441`](https://github.com/unipoll/api/commit/bd32441bab73e40be2adb1ee5c42de9530b7d5bd))

* Added scheme to update member ([`b5703c3`](https://github.com/unipoll/api/commit/b5703c3509eb7061c4581e9460f71f059ca87540))

* Added route to get member info and update member&#39;s role ([`1ec93ec`](https://github.com/unipoll/api/commit/1ec93ecef8dafa476218c2d1a874481e7e2a74b0))

* Added route to get personal group, cleaned files ([`431547e`](https://github.com/unipoll/api/commit/431547ec450614941bbadc24f6741c33d04e34f2))

* Merge pull request #28 from mike-pisman/Accounts

Added delete /users/me route ([`1ed7fcf`](https://github.com/unipoll/api/commit/1ed7fcf738c1892d15f68aae58e594b83b668278))

* Merge branch &#39;Testing&#39; into Accounts ([`b8c5674`](https://github.com/unipoll/api/commit/b8c5674bb835bd8dfc0edb932c30ec6bd125ef99))

* Added delete /users/me route ([`7ed1f69`](https://github.com/unipoll/api/commit/7ed1f6978bba74e98b41b46d0086d9e09e4383af))

* Fixed mypy error ([`d377361`](https://github.com/unipoll/api/commit/d37736155883aafc806254e763964722ab08546a))

* Changed FIXME to BUG ([`eaa61e9`](https://github.com/unipoll/api/commit/eaa61e97b306260b67d3983016722ec6894347ce))

* Added pydantic plugin for mypy ([`2bc21d2`](https://github.com/unipoll/api/commit/2bc21d2ace9329c52ae16edcb8d6ae08076ee839))

* Changed tests to run only on pull into Development ([`651adc7`](https://github.com/unipoll/api/commit/651adc7e6d906ba72a0542f128b54fb311b839ea))

* Added the badge for tests ([`d38d3fc`](https://github.com/unipoll/api/commit/d38d3fce5790396bfd90d7d9ef7b918a3cb4e665))

* Fixed issue with muliple directories when building ([`b436733`](https://github.com/unipoll/api/commit/b436733aecedb4763032fc08923f591a21e4c9a0))

* Merge pull request #26 from mike-pisman/Testing

Updates and Github actions ([`2d07a9a`](https://github.com/unipoll/api/commit/2d07a9aa4552b207a72f2d86dc27840e4ea1c1a6))

* Cleaned up files, fixed issues with UserID ([`b5b454f`](https://github.com/unipoll/api/commit/b5b454f3f5f4f6a82d76e43af2bdbfa696aec1ae))

* Merge pull request #25 from mike-pisman:Groups

Merge pull request #24 from mike-pisman:Accounts ([`3a9f88c`](https://github.com/unipoll/api/commit/3a9f88c17a97425b6271003932ae13dd78d4dfe6))

* Merge pull request #24 from mike-pisman:Accounts

Removed testing on pull, test only on push ([`d1fc772`](https://github.com/unipoll/api/commit/d1fc772c9edb0a928a906f19ba23826d2dd76a47))

* Replaced PydanticObjectId for GroupID ([`b6acbeb`](https://github.com/unipoll/api/commit/b6acbeb353ab6fb98e0a67f55304ac16eea18b45))

* Replaced PydanticObjectId with UserID ([`b1ef77f`](https://github.com/unipoll/api/commit/b1ef77f00a55c51972abb14303953abbebefeaea))

* Removed testing on pull, test only on push ([`30770ce`](https://github.com/unipoll/api/commit/30770ce968d5632dbc22938015e1f9d1fc6cf8cd))

* Updated node versions ([`08de6d0`](https://github.com/unipoll/api/commit/08de6d0ec8b034b372ba4fc44aef608f94b42927))

* Removed database test, updated Github workflow ([`b6b3bb5`](https://github.com/unipoll/api/commit/b6b3bb5800c55a260cc85968d239a1137483013b))

* Removed redundant  .env creation ([`9c76543`](https://github.com/unipoll/api/commit/9c765439075c1773c8ddd0dc851135a97860419b))

* Added MONGODB_URL to tox ([`e35b78b`](https://github.com/unipoll/api/commit/e35b78ba6fd82895ae8ad227b7ae6736614d7222))

* Added test to check database connection ([`26dad87`](https://github.com/unipoll/api/commit/26dad87701a50af374c5de7d44283c1ee8c7fcee))

* Added Postman integration ([`71df669`](https://github.com/unipoll/api/commit/71df6692e3522fcf0ff20373ab15cdc58c7f6b56))

* Fixed incorrect fastapi-users import ([`66b7841`](https://github.com/unipoll/api/commit/66b7841143d5fe2962ebe5dfb380b55dc5479aaf))

* Added debug for .env to check what&#39;s causing a failure ([`dc1ee52`](https://github.com/unipoll/api/commit/dc1ee5277c68869c1179abe3df4c3ec6fa6b2d40))

* Fixed .env ([`37d9a0a`](https://github.com/unipoll/api/commit/37d9a0a57cd1221e9dd8bd3255d371d807e45428))

* Added MongoDB connection url as .env file entry ([`3fac4cb`](https://github.com/unipoll/api/commit/3fac4cbed1550431b23a785fc05bc5aba13669ad))

* Added the comma that was causing the test failure
Removed py39, as it is too old ([`132e477`](https://github.com/unipoll/api/commit/132e47789a50989eb2f1687306bebb1876ec219b))

* Changed python version to string(yaml specifics) ([`8172690`](https://github.com/unipoll/api/commit/8172690dab5743fe3c18ba2a452e2774f1164435))

* Changed the action to run on push ([`f5924fd`](https://github.com/unipoll/api/commit/f5924fd9c4e21dde04af231c515fa1df8e7ad1e8))

* Merge pull request #23 from mike-pisman/Testing

Pulling changes to Development version 0.0.5 ([`1762bbf`](https://github.com/unipoll/api/commit/1762bbfda890056a5a2fc3ab54cd8dc62bca770c))

* Created Tests GitHub action ([`41c64ee`](https://github.com/unipoll/api/commit/41c64eef9b533d4279a21010f7cb5bca198feff5))

* Cleaned the files ([`277d3c5`](https://github.com/unipoll/api/commit/277d3c5ee4705d0261804915ed30924a81c323bc))

* removed git -e entry that was casing an error ([`18edca4`](https://github.com/unipoll/api/commit/18edca424461ac8f6efbbb18bffd8e4a5c52cff2))

* Fixed issue with author format ([`72cf89d`](https://github.com/unipoll/api/commit/72cf89dc48c62863a721f26450b94c0e79cbdc91))

* setup.py is no longer needed ([`3df063d`](https://github.com/unipoll/api/commit/3df063d19f4cfafbe9b2e2fafa77110cc01d1dd7))

* Added basic tox and setuptools configuration ([`49b9053`](https://github.com/unipoll/api/commit/49b90533a9ccb44c99fd08387113823ba00cd2ed))

* Cleaned the file for mypy and flake8 ([`24261f2`](https://github.com/unipoll/api/commit/24261f254c316a105bd1cb257760ad4e40f852bc))

* Added requirements_dev.txt for development/testing ([`13eb628`](https://github.com/unipoll/api/commit/13eb6289faab5049c2bee716f8d18ba5b22d4aef))

* Changed imports to avoid styling issues ([`3279770`](https://github.com/unipoll/api/commit/3279770f0ad1c12089ff9e51fc5d78ac90a26148))

* Added pytest-cov plugin ([`2b987f4`](https://github.com/unipoll/api/commit/2b987f48e70bfc7bd4c1f67d91a700cf15b1cf22))

* Moved tests outside of the app directory
Added response types
Changed print statement to use colored_debug
Added test_delete_group_no_owner()
Cleaned the files for mypy and flake8 ([`9c39fc1`](https://github.com/unipoll/api/commit/9c39fc158fb8c36b95d07af6f4eff1edea3d2afc))

* removed trailing space ([`359bd01`](https://github.com/unipoll/api/commit/359bd01809675f363eb1ada5e01bf1b29a4c3ef7))

* Added response types and cleaned the files for mypy and flake8 ([`2d62228`](https://github.com/unipoll/api/commit/2d622287fee2c29aaa80ddeac04823a450ec7783))

* Fixed import issue, cleaned the file ([`a0fb46d`](https://github.com/unipoll/api/commit/a0fb46dbd5f43d52c006a38c19a01672da5b302c))

* Merge pull request #22 from mike-pisman:Groups

No changes need review, update Groups and Users. ([`c54d543`](https://github.com/unipoll/api/commit/c54d54328cc61d7b61cbd4794889668b3aaef1e2))

* Updated response models, cleaned files for mypy and flake8 ([`1a72a4d`](https://github.com/unipoll/api/commit/1a72a4d82f45105d05466529c658ed459c78fc41))

* Added settings.json to repo ([`56871e9`](https://github.com/unipoll/api/commit/56871e934335dafac58b296e83f7f1469a351603))

* Merge pull request #21 from mike-pisman/Accounts

Add Account&#39;s updates to Groups ([`1144158`](https://github.com/unipoll/api/commit/114415829289db3d9d48fc67fd320d15dbef70b5))

* Merge branch &#39;Groups&#39; into Accounts ([`d297e13`](https://github.com/unipoll/api/commit/d297e130982738e240cfcddbc25de1b0a1b08ca6))

* Accepted incoming changes ([`f1302b1`](https://github.com/unipoll/api/commit/f1302b1727faa959c31274cf545b5333c054a2b4))

* Added .history folder ([`f95c1d9`](https://github.com/unipoll/api/commit/f95c1d9d8236390db90d720c1c32a1fd50c79b23))

* Changed the response of list_user_groups(), cleaned the file ([`660de6b`](https://github.com/unipoll/api/commit/660de6b5f9272e969f944954881a3580afc710fe))

* Replaced print with colored print, cleaned the file ([`01c0569`](https://github.com/unipoll/api/commit/01c0569da02c07ebb01029a501c01c259fb6f89d))

* Cleaned files for mypy and flake8 ([`f71ec1a`](https://github.com/unipoll/api/commit/f71ec1a8f2c403e2c003cd777ce6f9654523d0a4))

* Changed email field from str to EmailStr ([`db84108`](https://github.com/unipoll/api/commit/db84108a4271a9ecba8ceb2161f9d3fdd14977c3))

* Improved group testing:
- Added tests during group creation
- Added testing for group deletion
- Added debug message for various actions ([`d4419e5`](https://github.com/unipoll/api/commit/d4419e589b44046a08149eaca251bccddc5711c6))

* Merge pull request #20 from mike-pisman:Groups

Fixed unit test to Add members to test group ([`0d2e272`](https://github.com/unipoll/api/commit/0d2e272269d8444bd38a367c502835147bcd7992))

* Made member routes to exclusive
Updated routes to use new schemas for members ([`737cc5c`](https://github.com/unipoll/api/commit/737cc5ccd1e52ace9fdb656609f2e615616ed779))

* Update creation event to use colored debug ([`09fdf88`](https://github.com/unipoll/api/commit/09fdf8807bfb2b31c54d22f84f0415dcf01d0652))

* Updated Group schemas:
 - Added GroupReadSimple
 - Added GroupReadFull
 - Added GroupMember schema
 - Updated GroupReadMembers
 - Added examples ([`1723b33`](https://github.com/unipoll/api/commit/1723b3395cc8040bf594084999fee3630386eb5c))

* Fixed unit test to Add members to test group ([`08a1e78`](https://github.com/unipoll/api/commit/08a1e780804ef655c6976185b28f3c6c009d29af))

* Merge pull request #19 from mike-pisman:Groups

Update Group rouing and functionality ([`64b7003`](https://github.com/unipoll/api/commit/64b70030f1d3cdf765556b698c2413eab0f0ec38))

* Changed print to colored debug ([`c5e3f70`](https://github.com/unipoll/api/commit/c5e3f70b291a4f4b51ed003437ba98f2205c3c7c))

* Added GET users request, changed tags ([`991b140`](https://github.com/unipoll/api/commit/991b14057efe46adf10cb81951c8b974937bcfc0))

* Merge pull request #18 from mike-pisman/Groups

Groups ([`df823a2`](https://github.com/unipoll/api/commit/df823a20f7b29fd2c99e80d8263a1d0bff502f67))

* Merge pull request #17 from mike-pisman/Groups

Groups ([`7fde29b`](https://github.com/unipoll/api/commit/7fde29b1fd0ddde21da3dff70eec0e0c977fd134))

* Merge branch &#39;Development&#39; into Groups ([`7dd3577`](https://github.com/unipoll/api/commit/7dd35777d99bab042592e306f88c5fbd67f1f0ad))

* Merge pull request #16 from mike-pisman/Testing

Testing ([`b02391b`](https://github.com/unipoll/api/commit/b02391b701763bba3e0cdf5b89130a5dfa3284cc))

* Updated .gitignore ([`d748ffa`](https://github.com/unipoll/api/commit/d748ffa8695c5a68a635061fa95f2d014cce387f))

* Updated create_group ([`5110a59`](https://github.com/unipoll/api/commit/5110a592b36a4e1534819bf266eedd3037993253))

* Updated group_test ([`55445b5`](https://github.com/unipoll/api/commit/55445b51d21dc577b06e46891c4520b9c2c3ea60))

* Removed the work in progress ([`c1937c9`](https://github.com/unipoll/api/commit/c1937c92751bf1cd4ee3a45cc609d5d6f7030cf6))

* Merge pull request #15 from mike-pisman/Groups

Fixed bug with User.update ([`644dfd1`](https://github.com/unipoll/api/commit/644dfd13d71ee9b000c494457b222f17c19f247e))

* Fixed bug with User.update ([`607c8a0`](https://github.com/unipoll/api/commit/607c8a0093d36702e655c2e54e8e55810b14b073))

* Updated Group test ([`470711d`](https://github.com/unipoll/api/commit/470711df07792137dc99f86cda86f067ce749ce4))

* Updated .gitignore ([`a230cb5`](https://github.com/unipoll/api/commit/a230cb58d8d78378d6bff86b6866b0a2a278ab8b))

* Started working on group tests ([`63707cb`](https://github.com/unipoll/api/commit/63707cbcdbbea65bd510ab746ee43b2b2bf41bde))

* Added tests for user ([`5af074d`](https://github.com/unipoll/api/commit/5af074dff61acd31ffde5b00c2fef3b41c7b63cf))

* Added testing module ([`92332ca`](https://github.com/unipoll/api/commit/92332ca61ad5ea633898d461170231fab27971a5))

* Updated new group schemas ([`ae4a403`](https://github.com/unipoll/api/commit/ae4a4035ced81cfa366011e794401ca8988f6659))

* Added util function file for users ([`57e6a9c`](https://github.com/unipoll/api/commit/57e6a9cbec2161c68b25f0ba5fdc079d0efce229))

* Added new schemas: UserReadBasicInfo, UserAddToGroup
Added examples to schemas ([`4458112`](https://github.com/unipoll/api/commit/445811262a6c6687da01c0fc41eba6a146954c39))

* Major rework of group routes ([`ca08f25`](https://github.com/unipoll/api/commit/ca08f25a1f16c72d749799ae5b047fbd8e8ad7f0))

* Defined after_event to watch for updates ([`05cb5b1`](https://github.com/unipoll/api/commit/05cb5b10986549872759a41318356c245d404808))

* Updated UserNotFound to print different messages ([`70c821a`](https://github.com/unipoll/api/commit/70c821a0b2dd077dc09a25096277da6b3b8f4081))

* Added UserNotInGroup, updated status codes ([`117f76c`](https://github.com/unipoll/api/commit/117f76c24ad9f66673a04e70ae5fe1d19e239c44))

* Added reloading to uvicorn ([`d86460b`](https://github.com/unipoll/api/commit/d86460b19eca72ff3695030596e77fa553abb25f))

* Moved main to outer folder ([`5cf3b5f`](https://github.com/unipoll/api/commit/5cf3b5f0fa2c17d5588f135ff94c4727df3f74d4))

* Added Settings model for using with .env ([`c22fd15`](https://github.com/unipoll/api/commit/c22fd150febb267e571c9d4045e47ffbf60fa21c))

* Fixed tag spelling for login ([`239e153`](https://github.com/unipoll/api/commit/239e153514d3bcacc6fafdba7078b290510b85ac))

* Changed api version ([`28810b8`](https://github.com/unipoll/api/commit/28810b8c2f11a9551378b9ef760b5502a7672995))

* Updated Group schemas
Added config for examples and fields for validation ([`d1f0aa5`](https://github.com/unipoll/api/commit/d1f0aa50d3b75ab41766cf903e9b0d405dee310a))

* Improved group routes, work in progress
- GET &#34;/group?query&#34; with query works
- POST &#34;/group&#34; to create a group works ([`1960ffa`](https://github.com/unipoll/api/commit/1960ffa50006e42448a57fd7ca83bf2fe72d5e07))

* Cleaned Group model
Added field and basic validation ([`423acd7`](https://github.com/unipoll/api/commit/423acd78f122cf4a7859821e1eef2c09a2857cc4))

* Updated names of exceptions, Added GroupNotFound ([`dc454e4`](https://github.com/unipoll/api/commit/dc454e46d558c582c56ee4a57eeccda8d1df639f))

* Add test_venv to .gitignore ([`a92784d`](https://github.com/unipoll/api/commit/a92784d87c176d07930c0db564e0f7e6646175c0))

* Added get_user_groups() util function ([`b1e01ef`](https://github.com/unipoll/api/commit/b1e01ef2329833f3cd6dca62c9fd8dfe85257576))

* Added GroupList, GroupRead, GroupCreate schemas ([`f842ff1`](https://github.com/unipoll/api/commit/f842ff1a5072b63dd6727a0660bb01989b83b6ca))

* Added get /users/groups route ([`975fce1`](https://github.com/unipoll/api/commit/975fce190a7956e04678ffdf0f7e5963ed7857cb))

* Added first_name, last_name fields to User model ([`4b6d000`](https://github.com/unipoll/api/commit/4b6d0002f0f03ff96ddaefba7a703432d24e4655))

* Updated User schema to store first_name, last_name ([`b179755`](https://github.com/unipoll/api/commit/b179755175fe9d4029055099a8e93f5af153672f))

* Imported routes for cleaner set up ([`dcbef08`](https://github.com/unipoll/api/commit/dcbef08ae438772f91f84eb499f6adfe115d1f09))

* Added UserNotFound exception ([`298ceac`](https://github.com/unipoll/api/commit/298ceac8b6eda0c9b5a93ba4b671df3e3eab221f))

* Added classes for http exceptions ([`0ee1799`](https://github.com/unipoll/api/commit/0ee17996cb835bd94c9aee538bb60bf12f03eb54))

* Renamed Exceptions folder ([`27628d7`](https://github.com/unipoll/api/commit/27628d759c26f06f1679a2a929703b79ff884293))

* Renamed tags ([`d40fed6`](https://github.com/unipoll/api/commit/d40fed6616ca86c5274684beaf3199c41a9e2f49))

* Added functions to print colored messages ([`d6625d7`](https://github.com/unipoll/api/commit/d6625d7db7f019f75c0285b714b2ae1cb1b3502b))

* Created utlls folder ([`70b4ac4`](https://github.com/unipoll/api/commit/70b4ac4b4dd1b451e4b986475e469687d8e4e97e))

* Added  colorama ([`ad929c7`](https://github.com/unipoll/api/commit/ad929c7e17daf1d64a8baccbdd7ed354b96336fc))

* Fixed missing type ([`f23a5f5`](https://github.com/unipoll/api/commit/f23a5f529cab62ac00f23d1cbf96cf3635d54885))

* Improved Group retrieval for /grou GET ([`92765b5`](https://github.com/unipoll/api/commit/92765b5d174be7f13ffce5c848bcba34ccc450f5))

* Merge pull request #8 from mike-pisman/Accounts

Pulling changes from Accounts for Postman integration ([`eb1782f`](https://github.com/unipoll/api/commit/eb1782fa0cd2983c3a1430aa4865a97aebf96793))

* Added add_user() to Group model ([`158db53`](https://github.com/unipoll/api/commit/158db538dbf9509534df952bc4fc3b41c82cf693))

* Started add_user_to_group() ([`8171447`](https://github.com/unipoll/api/commit/817144707668cd2721a2cc0f8f66ddc9edf499b2))

* Temporarely changed groups type from Dict to List ([`f77b0aa`](https://github.com/unipoll/api/commit/f77b0aa96ef86c7c45b10eef2d7672180ef2a4c5))

* Added defenition for user deletion method ([`5cf2d32`](https://github.com/unipoll/api/commit/5cf2d32182d9b9c94dd2cce302a1cb709785c110))

* Created folder for storing custom exceptions ([`cb9b0bb`](https://github.com/unipoll/api/commit/cb9b0bb20087be7bc3d8d3da23e3b6f7d41a5f2c))

* Added init to schemas ([`225776d`](https://github.com/unipoll/api/commit/225776da9f9f7912dc64db844e94f9e16738c01e))

* Added a group exception user_exists ([`84a8f9e`](https://github.com/unipoll/api/commit/84a8f9e3abf86243d28a7231b8e0a1584452d9c3))

* Reworked group routes:
 - added /post to create a new group
 - Added /get to get all groups user belongs to ([`9d94e7e`](https://github.com/unipoll/api/commit/9d94e7ef35c14e6ec9ed2dc147064a41072d9bfc))

* changed owner from User to PydanticObjectId ([`e99de90`](https://github.com/unipoll/api/commit/e99de90c77a5ada07e331ca13991494618cbc8d1))

* Renamed Database ([`978a9ad`](https://github.com/unipoll/api/commit/978a9adf55d1183332368acf44bf7e997a5838ad))

* Fixed bug &#34;no Group class&#34; ([`168943c`](https://github.com/unipoll/api/commit/168943ca9386ddbc6bcaff5ea5256486396abd8a))

* Added group router ([`a301671`](https://github.com/unipoll/api/commit/a301671a8926ae08429a8cd6855136eebde5a5b1))

* Added requirements.txt ([`c0dca11`](https://github.com/unipoll/api/commit/c0dca11aa7d2c2aa7cfb0c589fcf7c9228dc6338))

* Cleaned up files ([`97dd184`](https://github.com/unipoll/api/commit/97dd18402b97e9b845c00aec6b8b93e50a16c831))

* Added Group model and started working on routes ([`4558f0d`](https://github.com/unipoll/api/commit/4558f0d0a21021d32e4b8bb63bc04df0f9b14bd8))

* Added routes for users ([`3b68fcb`](https://github.com/unipoll/api/commit/3b68fcb03999a8bd8452573edf7e4b97461f436c))

* Added init.py files to create modules ([`a7f4f5a`](https://github.com/unipoll/api/commit/a7f4f5acdbb28b0539e057a9433592d2e21c7ddb))

* Organized project using modules ([`6677b10`](https://github.com/unipoll/api/commit/6677b10fb35bdef9dbc4b1f24f7d11a19eba3e49))

* Created a separate main to run uvicorn ([`7c5b486`](https://github.com/unipoll/api/commit/7c5b486c4449c4333950b211e226a5964d5c13f1))

* Moved application definitions to app.py ([`67d018c`](https://github.com/unipoll/api/commit/67d018cb5ab04636fb33ce2bf36b0d1531a0b197))

* Basic main ([`d922477`](https://github.com/unipoll/api/commit/d9224775065a78cdc94bf0c1b2cf396fdef05c92))

* Basic MongoDB ([`b7795cf`](https://github.com/unipoll/api/commit/b7795cf9842ceb4ea20a791eaa8d8485a0cbf15c))

* Initial commit ([`becb151`](https://github.com/unipoll/api/commit/becb151b2225e962137a271746cb6a7a9a202e74))
