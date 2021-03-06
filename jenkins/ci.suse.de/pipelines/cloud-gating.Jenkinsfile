/**
 * The cloud-gating Jenkins Pipeline
 */

def ardana_lib = null

pipeline {
  // skip the default checkout, because we want to use a custom path
  options {
    skipDefaultCheckout()
    timestamps()
  }

  agent {
    node {
      label 'cloud-trigger'
      customWorkspace "${JOB_NAME}-${BUILD_NUMBER}"
    }
  }

  stages {

    stage('Setup workspace') {
      steps {
        script {
          env.staging_url = "http://provo-clouddata.cloud.suse.de/repos/x86_64/SUSE-OpenStack-Cloud-${version}-devel-staging/media.1/build"
          env.staging_build = sh (
            returnStdout: true,
            script: "wget -q -O - $staging_url | grep -oP 'Build[0-9]+'"
          ).trim()
          currentBuild.displayName = "#${BUILD_NUMBER}: ${staging_build}"

          sh('''
            git clone $git_automation_repo --branch $git_automation_branch automation-git
          ''')

          env.starttime = sh (
            returnStdout: true,
            script: '''
              rfcdate="$( curl -sI $staging_url | grep 'Last-Modified: ' | head -n1 | cut -d' ' -f2- )"
              epoch=$(date +%s -d "$rfcdate")
              if test "$epoch" -lt "1400000000"; then
                echo "Last-Modified epoch is too low to be valid."
                exit 1
              fi
              echo $epoch
            '''
          ).trim()

          cloud_lib = load "$WORKSPACE/automation-git/jenkins/ci.suse.de/pipelines/openstack-cloud.groovy"
          cloud_lib.load_extra_params_as_vars(extra_params)
        }
      }
    }

    stage('Trigger validation jobs') {
      // Do not abort all stages if one of them fails
      failFast false
      parallel {

        stage('Run cloud deploy job') {
          when {
            expression { deploy == 'true' }
          }
          steps {
            script {
              // reserve a resource here for the integration job, to avoid
              // keeping a cloud-ardana-ci worker busy while waiting for a
              // resource to become available.
              cloud_lib.run_with_reserved_env(true, cloud_env, null) {
                reserved_env ->
                cloud_lib.trigger_build("cloud-ardana${version}-job-entry-scale-kvm-x86_64", [
                  string(name: 'cloud_env', value: reserved_env),
                  string(name: 'reserve_env', value: "false"),
                  string(name: 'cleanup', value: "never"),
                  string(name: 'rc_notify', value: "true"),
                  string(name: 'git_automation_repo', value: "$git_automation_repo"),
                  string(name: 'git_automation_branch', value: "$git_automation_branch"),
                  text(name: 'extra_params', value: extra_params)
                ], false)
              }
            }
          }
        }

        stage('Run cloud update job') {
          when {
            expression { deploy_and_update == 'true' }
          }
          steps {
            script {
              // reserve a resource here for the integration job, to avoid
              // keeping a cloud-ardana-ci worker busy while waiting for a
              // resource to become available.
              cloud_lib.run_with_reserved_env(true, cloud_env, null) {
                reserved_env ->
                cloud_lib.trigger_build("cloud-ardana${version}-job-entry-scale-kvm-update-x86_64", [
                  string(name: 'cloud_env', value: reserved_env),
                  string(name: 'reserve_env', value: "false"),
                  string(name: 'cleanup', value: "never"),
                  string(name: 'rc_notify', value: "true"),
                  string(name: 'git_automation_repo', value: "$git_automation_repo"),
                  string(name: 'git_automation_branch', value: "$git_automation_branch"),
                  text(name: 'extra_params', value: extra_params)
                ], false)
              }
            }
          }
        }
      }
    }

    stage('Submit project') {
      steps {
        script{
          cloud_lib.trigger_build("openstack-submit-project", [
            string(name: 'project', value: "Devel:Cloud:${version}"),
            string(name: 'starttime', value: "${starttime}"),
            string(name: 'subproject', value: "Staging"),
            string(name: 'package_whitelist', value: "ardana venv"),
            string(name: 'package_blacklist', value: "crowbar")
          ])
        }
      }
    }

  }
  post {
    cleanup {
      cleanWs()
    }
  }
}
