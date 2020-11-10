<template>
    <div>
        <nav-bar></nav-bar>
        <br>
        <div class="container-fluid justify-content-center">
            <div class="experiment-form">
                <b-form action="/experiment">
                    <b-form-group
                        id="input-group"
                        label="Experiment Code:"
                        label-for="input"
                    >
                        <b-form-input
                            name="code"
                            id="input"
                            v-model="experiment_code"
                            type="text"
                            :maxlength="4"
                            required
                            placeholder="Code"
                            @input="onInput"
                        ></b-form-input>
                    </b-form-group>
                    <b-button type="submit" class="btn btn-block" variant="primary">Submit</b-button>
                </b-form>
            </div>
        </div>
  
        <!-- <form action="{% url 'gestureApp:experiment' %}">
            {{form.as_p}}
            <input type="submit" value="Enter">
        </form> -->
    </div>
    
</template>

<script>
module.exports = {
  data: function () {
    return {
        experiment_code: '',
    };
  },
  props: {
  },
  mounted: function () {
  },
  components: {
      'nav-bar': httpVueLoader('/static/gestureApp/js/components/NavBar.vue'),
  },
  computed: {},
  watch: {},
  methods: {
      onInput: function(input) {
          this.experiment_code = input.toUpperCase();
      }
  },
};
</script>

<style scoped>
    .experiment-form {
        border: 1px solid lightgray;
        width: 250px;
        padding: 40px;
        float: none;
        margin: 0 auto;
        border-radius: 5px;
    }
</style>
