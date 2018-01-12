
| [![Republic of Estonia Information System Authority](../img/ria_100_en.png)](https://www.ria.ee/en/) [![X-ROAD](../img/xroad_100_en.png)](https://www.ria.ee/en/x-road.html) | ![European Union / European Regional Development Fund / Investing in your future](../img/eu_rdf_100_en.png "Documents that are tagged with EU/SF logos must keep the logos until 1.11.2022. If it has not stated otherwise in the documentation. If new documentation is created  using EU/SF resources the logos must be tagged appropriately so that the deadline for logos could be found.") |
| :-------------------------------------------------- | -------------------------: |

# X-Road v6 monitor project - FactSheet Tests

### Test case 1: Query count
Description: The purpose of this test is to get the number of queries for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_query_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.

### Test case 2: Service count
Description: The purpose of this test is to get the number of services for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_service_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* Service = serviceCode, serviceVersion, serviceMemberCode, serviceMemberClass.
* The documents with "succeeded" = True should only be taken into consideration.

### Test case 3: Producer count
Description: The purpose of this test is to get the number of producers for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_producer_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* Producer = serviceXRoadInstance, serviceMemberClass, serviceMemberCode.
* The documents with "succeeded" = True should only be taken into consideration.

### Test case 4: Member count
Description: The purpose of this test is to get the number of members for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_member_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* Member = XRoadInstance, MemberClass, MemberCode
* The documents with "succeeded" = True should only be taken into consideration.

### Test case 5: GOV Member count
Description: The purpose of this test is to get the number of GOV members for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_member_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* Member = XRoadInstance, MemberClass, MemberCode
* GOV Member = "MemberClass" = "GOV"
* The documents with "succeeded" = True should only be taken into consideration.
* A unique GOV member is also a valid regular member.

### Test case 6: Subsystem count
Description: The purpose of this test is to get the number of subsystems for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_subsystem_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* Subsystem = XRoadInstance, MemberClass, MemberCode, SubsystemCode
* The documents with "succeeded" = True should only be taken into consideration.

### Test case 7: SecSrv count
Description: The purpose of this test is to get the number of security servers for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_subsystem_count

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* The documents with "succeeded" = True should only be taken into consideration.
* If the securityServerAddress is "None", then it will still be counted as a unique value.

### Test case 8: Producers top
Description: The purpose of this test is to get the given number of top producers for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_producers_top

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* The documents with "succeeded" = True should only be taken into consideration.

### Test case 9: Consumers top
Description: The purpose of this test is to get the given number of top consumers for specified time frame.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_get_consumers_top

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* The documents with "succeeded" = True should only be taken into consideration.

### Test case 10: Final FactSheet
Description: The purpose of this test is to test the final FactSheet.

Integration tests:

* /integration_tests/ci_reports/test_factsheet_manager_CI.py::TestFactSheetCI::test_create_results_document

Unit tests:

* Not applicable

Variations/notes:

* Documents that are not within the time frame are not queried and not added to the resulting count.
* If no matching documents found in the time frame, 0 must be returned.
* It must be possible to use either side of the pair (client/producer) for querying.
* The documents with "succeeded" = True should only be taken into consideration.
