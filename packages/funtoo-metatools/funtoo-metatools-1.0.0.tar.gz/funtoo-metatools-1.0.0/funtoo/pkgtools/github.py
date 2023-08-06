import re
import packaging.version

# tag_gen and release_gen are higher-level functions that return a dict of items, suitable for
# augmenting the pkginfo dict, and thus easy to integrate into yaml-based autogens.


async def release_gen(hub, github_user, github_repo, release_data=None, tarball=None, select=None, **kwargs):
	"""
	This method will query the GitHub API for releases for a specific project, find the most recent
	release, and then return a dictionary containing the keys "version", "artifacts" and "sha", which
	map to the latest non-prerelease version of the release, a list of an artifact associated with
	this release, and the SHA1 for the commit for this tagged release. This info can easily be added
	to the pkginfo dict.

	If 'tarball' (string) is specified, this method will look for a tarball in the release that matches
	the string. A literal '{version}' in the string will be replaced with the version of the release,
	so you will probably want to use that in your tarball string. If no tarball string is specified,
	we grab the source code by looking at the tag associated with the release, and grab a tarball for
	this particular tag.

	``release_data`` may contain the full decoded JSON of a query to the /releases endpoint, as returned
	by ``hub.pkgtools.fetch.get_page(url, is_json=True).`` Otherwise, this information will be queried
	directly from GitHub.

	``select`` may contain a regex string which specifies a pattern that must match the tag_name for
	it to be considered.
	"""
	if not release_data:
		release_data = await hub.pkgtools.fetch.get_page(f"https://api.github.com/repos/{github_user}/{github_repo}/releases", is_json=True)
	for release in release_data:
		if release['draft'] or release['prerelease']:
			continue
		if select and not re.match(select, release['tag_name']):
			continue
		match_obj = re.search('([0-9.]+)', release['tag_name'])
		if match_obj:
			version = match_obj.groups()[0]
		else:
			continue
		if tarball:
			# We are looking for a specific tarball:
			archive_name = tarball.format(version=version)
			for asset in release['assets']:
				if asset['name'] == archive_name:
					return {
						"version": version,
						"artifacts": [hub.pkgtools.ebuild.Artifact(url=asset['browser_download_url'], final_name=archive_name)]
					}
		else:
			# We want to grab the default tarball for the associated tag:
			desired_tag = release['tag_name']
			tag_data = await hub.pkgtools.fetch.get_page(f"https://api.github.com/repos/{github_user}/{github_repo}/tags", is_json=True)
			sha = next(filter(lambda tag_ent: tag_ent["name"] == desired_tag, tag_data))['commit']['sha']

			########################################################################################################
			# GitHub does not list this URL in the release's assets list, but it is always available if there is an
			# associated tag for the release. Rather than use the tag name (which would give us a non-distinct file
			# name), we use the sha1 to grab a specific URL and use a specific final name on disk for the artifact.
			########################################################################################################

			url = f"https://github.com/{github_user}/{github_repo}/tarball/{sha}"
			return {
				"version": version,
				"artifacts": [hub.pkgtools.ebuild.Artifact(url=url, final_name=f'{github_repo}-{version}-{sha[:7]}.tar.gz')],
				"sha": sha
			}


def iter_tag_versions(tags_list, select=None):
	"""
	This method iterates over each tag in tags_list, extracts the version information, and
	yields a tuple of that version as well as the entire GitHub tag data for that tag.

	``select`` specifies a regex string that must match for the tag version to be considered.
	"""
	for tag_data in tags_list:
		if select and not re.match(select, tag_data['name']):
			continue
		match = re.search('([0-9.]+)', tag_data['name'])
		if match:
			yield match.groups()[0], tag_data


async def latest_tag_version(hub, github_user, github_repo, tag_data=None, select=None):
	"""
	This method will look at all the tags in a repository, look for a version string in each tag,
	find the most recent version, and return the version and entire tag data as a tuple.

	``select`` specifies a regex string that must match for the tag version to be considered.

	If no matching versions, None is returned.
	"""
	if tag_data is None:
		tag_data = await hub.pkgtools.fetch.get_page(f"https://api.github.com/repos/{github_user}/{github_repo}/tags", is_json=True)
	versions_and_tag_elements = list(iter_tag_versions(tag_data, select=select))
	if not len(versions_and_tag_elements):
		return
	else:
		return max(versions_and_tag_elements, key=lambda v: packaging.version.parse(v[0]))


async def tag_gen(hub, github_user, github_repo, tag_data=None, select=None, **kwargs):
	"""
	Similar to ``release_gen``, this will query the GitHub API for the latest tagged version of a project,
	and return a dictionary that can be added to pkginfo containing the version, artifacts and commit sha.

	This method may return None if no suitable tags are found.
	"""
	result = await latest_tag_version(hub, github_user, github_repo, tag_data=tag_data, select=select)
	if result is None:
		return None
	version, tag_data = result
	sha = tag_data['commit']['sha']
	url = f"https://github.com/{github_user}/{github_repo}/tarball/{sha}"
	return {
		"version": version,
		"artifacts": [hub.pkgtools.ebuild.Artifact(url=url, final_name=f'{github_repo}-{version}-{sha[:7]}.tar.gz')],
		"sha": sha
	}
