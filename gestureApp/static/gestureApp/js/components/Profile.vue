<template>
  <div v-if="!isUserEmpty" class="container-fluid">
    <h1 class="text-center">Profile</h1>
    <a href="/profile/create_study" class="btn btn-lg text-center btn-primary"
      >Create Study</a
    >
    <a
      v-if="studies.length > 0"
      href="/profile/create_experiment"
      class="btn btn-lg text-center btn-primary"
      >Create Experiment</a
    >
    <br />
    <br />
    <!-- Unpublished studies -->
    <template v-if="unpublished_studies.length > 0">
      <h4>Unpublished studies:</h4>
      <div
        class="row mt-3"
        v-for="(study, std_index) in unpublished_studies"
        :key="study.code"
      >
        <b-card-group class="col">
          <b-card :header="`${study.name} (${study.code})`">
            <p v-if="study.description !== ''">{{ study.description }}</p>
            <p class="card-text mt-2">
              Study actions:
              <a :href="`/profile/study/edit/${study.code}`"> Edit </a>
              |
              <b-button
                class="p-0"
                variant="link"
                @click="$emit('delete-study', study.code)"
              >
                Delete
              </b-button>
              |
              <b-button
                class="p-0"
                variant="link"
                @click="$emit('duplicate-study', study.code)"
              >
                Duplicate
              </b-button>
              |
              <b-button
                class="p-0"
                variant="link"
                @click="$emit('publish-study', study.code)"
              >
                Publish
              </b-button>
            </p>
            <b-button
              v-b-toggle="'collapse_unpub_' + std_index"
              variant="primary"
              size="sm"
              >Show/hide Study</b-button
            >
            <b-collapse :id="'collapse_unpub_' + std_index" class="mt-2">
              <h6>New group</h6>
              <b-form inline>
                <b-form-input
                  id="inline-form-input-name"
                  v-model="group_name"
                  class="mb-2 mr-sm-2 mb-sm-0"
                  placeholder="Group name"
                ></b-form-input>
                <b-button
                  variant="primary"
                  @click="
                    $emit('new-group', group_name, study.code);
                    group_name = null;
                  "
                  >Save</b-button
                >
              </b-form>
              <br />
              <h5>Groups</h5>
              <div v-for="group in study.groups" :key="group.id">
                <h6 class="text-primary">
                  {{ group.name }} ({{ group.code }})
                </h6>
                <p class="card-text mt-2">
                  Group actions:
                  <!-- TODO: still missing -->
                  <a :href="`/profile/group/edit/${group.code}`"> Edit </a>
                  |
                  <b-button
                    class="p-0"
                    variant="link"
                    @click="$emit('delete-group', group.code)"
                  >
                    Delete
                  </b-button>
                </p>
                <b-list-group v-if="group.experiments.length > 0">
                  <b-list-group-item
                    v-for="(experiment, index) in group.experiments"
                    :key="'E' + experiment.code"
                    class="d-flex justify-content-between align-items-center"
                    >{{ index + 1 }}. {{ experiment.name }} ({{
                      experiment.code
                    }})
                    <span>
                      <a :href="`/profile/experiment/edit/${experiment.code}`">
                        Edit
                      </a>
                      |
                      <b-button
                        class="p-0"
                        variant="link"
                        @click="$emit('delete-experiment', experiment.code)"
                      >
                        Delete
                      </b-button>
                      |
                      <b-button
                        class="p-0"
                        variant="link"
                        @click="$emit('duplicate-experiment', experiment.code)"
                      >
                        Duplicate
                      </b-button>
                      |
                      <a :href="`/experiment/${experiment.code}`"
                        >Test Experiment</a
                      >
                      |
                      <a :href="'/raw_data/?code=' + experiment.code"
                        >Raw data</a
                      >
                      |
                      <a :href="'/processed_data/?code=' + experiment.code">
                        Processed data</a
                      >
                      |
                      <a
                        :href="
                          '/api/experiment/download_end_survey/' +
                          experiment.code
                        "
                      >
                        Survey data</a
                      >
                      |
                      <a
                        :href="
                          '/api/experiment/bonstrup_metrics/' + experiment.code
                        "
                      >
                        Bonstrup metrics</a
                      >
                      <b-badge
                        variant="primary"
                        pill
                        v-b-tooltip.hover
                        :title="experiment.responses + ' responses'"
                        >{{ experiment.responses }}</b-badge
                      >
                    </span></b-list-group-item
                  >
                </b-list-group>
                <p v-else>No experiments in this group.</p>
                <br />
              </div>
            </b-collapse>
          </b-card>
        </b-card-group>
      </div>
    </template>
    <br />
    <!-- Published Studies -->
    <template v-if="published_studies.length > 0">
      <h4>Published studies:</h4>
      <div
        class="row mt-3"
        v-for="(study, std_index_2) in published_studies"
        :key="study.code"
      >
        <b-card-group class="col">
          <b-card
            :header="`${study.name} (${study.code}) (${
              study.enabled ? 'enabled' : 'disabled'
            })`"
          >
            <p v-if="study.description !== ''">{{ study.description }}</p>
            <p class="card-text mt-2">
              Study actions:
              <a :href="`/profile/study/edit/${study.code}`"> View </a>
              |
              <b-button
                class="p-0"
                variant="link"
                @click="$emit('delete-study', study.code)"
              >
                Delete
              </b-button>
              |
              <b-button
                class="p-0"
                variant="link"
                @click="$emit('duplicate-study', study.code)"
              >
                Duplicate
              </b-button>
              |
              <b-button
                class="p-0"
                variant="link"
                v-if="study.enabled"
                @click="$emit('disable-study', study.code)"
                >Disable
              </b-button>
              <b-button
                class="p-0"
                variant="link"
                v-else
                @click="$emit('enable-study', study.code)"
                >Enable
              </b-button>
            </p>
            <b-button
              v-b-toggle="'collapse_pub_' + std_index_2"
              variant="primary"
              size="sm"
              >Show/hide Study</b-button
            >
            <b-collapse :id="'collapse_pub_' + std_index_2" class="mt-2">
              <h5>Groups</h5>
              <div v-for="group in study.groups" :key="group.id">
                <h6
                  :class="{
                    'text-primary': group.enabled,
                    'text-danger': !group.enabled,
                  }"
                >
                  {{ group.name }} ({{ group.code }}) ({{
                    group.enabled ? "enabled" : "disabled"
                  }})
                </h6>
                <p class="card-text mt-2">
                  Group actions:
                  <b-button
                    class="p-0"
                    variant="link"
                    @click="$emit('delete-group', group.code)"
                  >
                    Delete
                  </b-button>
                  |
                  <b-button
                    class="p-0"
                    variant="link"
                    v-if="group.enabled"
                    @click="$emit('disable-group', group.code)"
                    >Disable
                  </b-button>
                  <b-button
                    class="p-0"
                    variant="link"
                    v-else
                    @click="$emit('enable-group', group.code)"
                    >Enable
                  </b-button>
                </p>
                <b-list-group v-if="group.experiments.length > 0">
                  <b-list-group-item
                    v-for="(experiment, index) in study.experiments"
                    :key="'E' + experiment.code"
                    class="d-flex justify-content-between align-items-center"
                    >{{ index + 1 }}. {{ experiment.name }} ({{
                      experiment.code
                    }}) ({{ experiment.enabled ? "enabled" : "disabled" }})
                    <span>
                      <a :href="`/profile/experiment/edit/${experiment.code}`">
                        View
                      </a>
                      |
                      <b-button
                        class="p-0"
                        variant="link"
                        @click="$emit('delete-experiment', experiment.code)"
                      >
                        Delete
                      </b-button>
                      |
                      <b-button
                        class="p-0"
                        variant="link"
                        @click="$emit('duplicate-experiment', experiment.code)"
                      >
                        Duplicate
                      </b-button>
                      |
                      <b-button
                        class="p-0"
                        variant="link"
                        v-if="experiment.enabled"
                        @click="$emit('disable-experiment', experiment.code)"
                        >Disable
                      </b-button>
                      <b-button
                        class="p-0"
                        variant="link"
                        v-else
                        @click="$emit('enable-experiment', experiment.code)"
                        >Enable
                      </b-button>
                      |
                      <a :href="`/experiment/${experiment.code}`"
                        >Do Experiment</a
                      >
                      |
                      <a :href="'/raw_data/?code=' + experiment.code"
                        >Raw data</a
                      >
                      |
                      <a :href="'/processed_data/?code=' + experiment.code">
                        Processed data</a
                      >
                      |
                      <a
                        :href="
                          '/api/experiment/download_end_survey/' +
                          experiment.code
                        "
                      >
                        Survey data</a
                      >
                      |
                      <a
                        :href="
                          '/api/experiment/bonstrup_metrics/' + experiment.code
                        "
                      >
                        Bonstrup metrics</a
                      >
                      <b-badge
                        variant="primary"
                        pill
                        v-b-tooltip.hover
                        :title="experiment.responses + ' responses'"
                        >{{ experiment.responses }}</b-badge
                      >
                    </span></b-list-group-item
                  ></b-list-group
                >
                <p v-else>No experiments in this group.</p>
                <br />
              </div>
            </b-collapse>
          </b-card>
        </b-card-group>
      </div>
    </template>
    <br />

    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      group_name: null,
    };
  },
  props: {
    current_user: Object,
    studies: Array,
  },
  mounted: function () {},
  components: {},
  computed: {
    published_studies() {
      return this.studies.filter((s) => s.published);
    },
    unpublished_studies() {
      return this.studies.filter((s) => !s.published);
    },
    isUserEmpty() {
      return (
        Object.keys(this.current_user).length === 0 &&
        this.current_user.constructor === Object
      );
    },
  },
  watch: {},
  methods: {
    isObjectEmpty: function (obj) {
      return Object.keys(obj).length === 0 && obj.constructor === Object;
    },
  },
};
</script>

<style scoped></style>
